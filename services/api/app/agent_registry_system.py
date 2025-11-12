"""
Global Agent Registry System
Tracks all production agents with cryptographic identity, ownership, and safety ratings
"""
import json
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import sqlite3


class SafetyRating(Enum):
    """Agent safety rating levels"""
    UNSAFE = 1           # 0-3.9/10 - Critical failures, do not deploy
    POOR = 2             # 4.0-5.4/10 - Major safety concerns
    MODERATE = 3         # 5.5-6.9/10 - Some concerns, monitor closely
    GOOD = 4             # 7.0-8.4/10 - Generally safe
    EXCELLENT = 5        # 8.5-10/10 - Exceptional safety


class AgentStatus(Enum):
    """Agent deployment status"""
    PENDING_CERTIFICATION = "pending_certification"
    CERTIFIED = "certified"
    PRODUCTION = "production"
    SUSPENDED = "suspended"
    RECALLED = "recalled"
    REVOKED = "revoked"


class ReportSeverity(Enum):
    """Severity of behavior reports"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentOwner:
    """Agent owner information"""
    owner_id: str
    organization: str
    email: str
    phone: Optional[str] = None
    verified: bool = False


@dataclass
class AgentCertificate:
    """Cryptographically signed agent certificate"""
    agent_id: str
    agent_name: str
    model: str
    owner_id: str
    safety_rating: int
    safety_score: float
    test_results: Dict
    issued_at: str
    expires_at: str
    signature: str
    status: str = AgentStatus.CERTIFIED.value


@dataclass
class BehaviorReport:
    """User/agent report of misbehavior"""
    report_id: str
    agent_id: str
    reporter_type: str  # "human" or "agent"
    reporter_id: str
    severity: str
    violation_type: str
    description: str
    evidence: Optional[Dict] = None
    reported_at: str = None
    status: str = "pending"  # pending, investigating, confirmed, dismissed

    def __post_init__(self):
        if not self.reported_at:
            self.reported_at = datetime.now().isoformat()


class GlobalAgentRegistry:
    """Central registry for all production agents"""

    def __init__(self, db_path: str = "agent_registry.db", secret_key: str = "production-secret"):
        self.db_path = db_path
        self.secret_key = secret_key
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Owners table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS owners (
                owner_id TEXT PRIMARY KEY,
                organization TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                verified INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # Agents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                model TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                safety_rating INTEGER NOT NULL,
                safety_score REAL NOT NULL,
                test_results TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                signature TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES owners(owner_id)
            )
        """)

        # Behavior reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_reports (
                report_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                reporter_type TEXT NOT NULL,
                reporter_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                violation_type TEXT NOT NULL,
                description TEXT NOT NULL,
                evidence TEXT,
                reported_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        # Agent status history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                old_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                reason TEXT,
                changed_at TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        # Owner notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                read INTEGER DEFAULT 0,
                FOREIGN KEY (owner_id) REFERENCES owners(owner_id),
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        conn.commit()
        conn.close()

    def register_owner(self, owner: AgentOwner) -> bool:
        """Register a new agent owner"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO owners (owner_id, organization, email, phone, verified, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                owner.owner_id,
                owner.organization,
                owner.email,
                owner.phone,
                1 if owner.verified else 0,
                datetime.now().isoformat()
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def register_agent(self, certificate: AgentCertificate) -> bool:
        """Register a certified agent in the global registry"""
        # Verify signature
        if not self._verify_signature(certificate):
            raise ValueError("Invalid certificate signature")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO agents (
                    agent_id, agent_name, model, owner_id, safety_rating,
                    safety_score, test_results, issued_at, expires_at,
                    signature, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                certificate.agent_id,
                certificate.agent_name,
                certificate.model,
                certificate.owner_id,
                certificate.safety_rating,
                certificate.safety_score,
                json.dumps(certificate.test_results),
                certificate.issued_at,
                certificate.expires_at,
                certificate.signature,
                certificate.status
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, o.organization, o.email
            FROM agents a
            JOIN owners o ON a.owner_id = o.owner_id
            WHERE a.agent_id = ?
        """, (agent_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "agent_id": row[0],
                "agent_name": row[1],
                "model": row[2],
                "owner_id": row[3],
                "safety_rating": row[4],
                "safety_score": row[5],
                "test_results": json.loads(row[6]),
                "issued_at": row[7],
                "expires_at": row[8],
                "signature": row[9],
                "status": row[10],
                "owner_organization": row[11],
                "owner_email": row[12]
            }
        return None

    def report_behavior(self, report: BehaviorReport) -> str:
        """Submit a behavior report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Generate report ID
        report.report_id = hashlib.sha256(
            f"{report.agent_id}{report.reporter_id}{report.reported_at}".encode()
        ).hexdigest()[:16]

        cursor.execute("""
            INSERT INTO behavior_reports (
                report_id, agent_id, reporter_type, reporter_id,
                severity, violation_type, description, evidence,
                reported_at, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.report_id,
            report.agent_id,
            report.reporter_type,
            report.reporter_id,
            report.severity,
            report.violation_type,
            report.description,
            json.dumps(report.evidence) if report.evidence else None,
            report.reported_at,
            report.status
        ))

        conn.commit()
        conn.close()

        # Check if agent should be auto-suspended
        self._evaluate_reports(report.agent_id)

        return report.report_id

    def _evaluate_reports(self, agent_id: str):
        """Evaluate if agent should be suspended based on reports"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count recent reports
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM behavior_reports
            WHERE agent_id = ?
            AND status = 'pending'
            AND datetime(reported_at) > datetime('now', '-7 days')
            GROUP BY severity
        """, (agent_id,))

        severity_counts = dict(cursor.fetchall())

        # Auto-suspend rules
        critical_count = severity_counts.get("critical", 0)
        high_count = severity_counts.get("high", 0)

        should_suspend = (
            critical_count >= 1 or  # Any critical report
            high_count >= 3 or      # 3+ high severity reports
            sum(severity_counts.values()) >= 10  # 10+ total reports
        )

        if should_suspend:
            self.update_agent_status(
                agent_id,
                AgentStatus.SUSPENDED,
                f"Auto-suspended: {critical_count} critical, {high_count} high severity reports"
            )

        conn.close()

    def update_agent_status(self, agent_id: str, new_status: AgentStatus, reason: str):
        """Update agent status and notify owner"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current status and owner
        cursor.execute("SELECT status, owner_id FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return

        old_status, owner_id = row

        # Update status
        cursor.execute("""
            UPDATE agents SET status = ? WHERE agent_id = ?
        """, (new_status.value, agent_id))

        # Record history
        cursor.execute("""
            INSERT INTO status_history (agent_id, old_status, new_status, reason, changed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (agent_id, old_status, new_status.value, reason, datetime.now().isoformat()))

        # Notify owner
        if new_status in [AgentStatus.SUSPENDED, AgentStatus.RECALLED]:
            message = f"URGENT: Agent {agent_id} has been {new_status.value.upper()}. Reason: {reason}. Please pull from production immediately and contact support."
            cursor.execute("""
                INSERT INTO notifications (owner_id, agent_id, type, message, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (owner_id, agent_id, new_status.value, message, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def recall_agent(self, agent_id: str, reason: str):
        """Recall an agent from production"""
        self.update_agent_status(agent_id, AgentStatus.RECALLED, reason)

    def get_reports_for_agent(self, agent_id: str) -> List[Dict]:
        """Get all behavior reports for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM behavior_reports
            WHERE agent_id = ?
            ORDER BY reported_at DESC
        """, (agent_id,))

        rows = cursor.fetchall()
        conn.close()

        return [{
            "report_id": row[0],
            "agent_id": row[1],
            "reporter_type": row[2],
            "reporter_id": row[3],
            "severity": row[4],
            "violation_type": row[5],
            "description": row[6],
            "evidence": json.loads(row[7]) if row[7] else None,
            "reported_at": row[8],
            "status": row[9]
        } for row in rows]

    def get_owner_notifications(self, owner_id: str, unread_only: bool = False) -> List[Dict]:
        """Get notifications for an owner"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT * FROM notifications
            WHERE owner_id = ?
        """
        if unread_only:
            query += " AND read = 0"
        query += " ORDER BY created_at DESC"

        cursor.execute(query, (owner_id,))
        rows = cursor.fetchall()
        conn.close()

        return [{
            "id": row[0],
            "owner_id": row[1],
            "agent_id": row[2],
            "type": row[3],
            "message": row[4],
            "created_at": row[5],
            "read": bool(row[6])
        } for row in rows]

    def get_production_agents(self) -> List[Dict]:
        """Get all agents currently in production"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, o.organization
            FROM agents a
            JOIN owners o ON a.owner_id = o.owner_id
            WHERE a.status = ?
        """, (AgentStatus.PRODUCTION.value,))

        rows = cursor.fetchall()
        conn.close()

        return [{
            "agent_id": row[0],
            "agent_name": row[1],
            "model": row[2],
            "owner_id": row[3],
            "safety_rating": row[4],
            "safety_score": row[5],
            "status": row[10],
            "organization": row[11]
        } for row in rows]

    def _verify_signature(self, certificate: AgentCertificate) -> bool:
        """Verify certificate signature"""
        metadata = f"{certificate.agent_id}|{certificate.agent_name}|{certificate.model}|{certificate.safety_rating}|{certificate.issued_at}"
        expected_sig = hmac.new(
            self.secret_key.encode(),
            metadata.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, certificate.signature)

    def get_stats(self) -> Dict:
        """Get registry statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total agents by status
        cursor.execute("""
            SELECT status, COUNT(*) FROM agents GROUP BY status
        """)
        stats["agents_by_status"] = dict(cursor.fetchall())

        # Total reports by severity
        cursor.execute("""
            SELECT severity, COUNT(*) FROM behavior_reports GROUP BY severity
        """)
        stats["reports_by_severity"] = dict(cursor.fetchall())

        # Average safety rating
        cursor.execute("SELECT AVG(safety_rating) FROM agents")
        stats["avg_safety_rating"] = cursor.fetchone()[0]

        # Total owners
        cursor.execute("SELECT COUNT(*) FROM owners")
        stats["total_owners"] = cursor.fetchone()[0]

        conn.close()
        return stats


# Example usage
if __name__ == "__main__":
    # Initialize registry
    registry = GlobalAgentRegistry()

    # Register owner
    owner = AgentOwner(
        owner_id="owner-001",
        organization="Acme AI Inc",
        email="safety@acmeai.com",
        phone="+1-555-0123",
        verified=True
    )
    registry.register_owner(owner)

    # Register agent
    from agent_safety_rating_system import AgentCertificationAuthority

    ca = AgentCertificationAuthority("production-secret")
    certificate = ca.issue_certificate(
        agent_name="Claude Haiku Child Safety Agent",
        model="claude-3-5-haiku-20241022",
        safety_score=8.0,
        test_results={"total_scenarios": 100, "critical_failures": 0, "high_failures": 2}
    )

    # Add owner and status
    certificate.owner_id = "owner-001"
    certificate.status = AgentStatus.PRODUCTION.value

    registry.register_agent(certificate)

    print(f"✅ Agent registered: {certificate.agent_id}")
    print(f"   Owner: {owner.organization}")
    print(f"   Rating: {certificate.safety_rating}/5")
    print(f"   Status: {certificate.status}")

    # Simulate behavior report
    report = BehaviorReport(
        report_id="",  # Will be generated
        agent_id=certificate.agent_id,
        reporter_type="human",
        reporter_id="user-12345",
        severity=ReportSeverity.HIGH.value,
        violation_type="privacy_violation",
        description="Agent asked for home address from 8-year-old",
        evidence={"conversation_id": "conv-789", "timestamp": datetime.now().isoformat()}
    )

    report_id = registry.report_behavior(report)
    print(f"\n⚠️  Behavior reported: {report_id}")

    # Check agent status
    agent = registry.get_agent(certificate.agent_id)
    print(f"   Agent status after report: {agent['status']}")

    # Check owner notifications
    notifications = registry.get_owner_notifications("owner-001", unread_only=True)
    print(f"\n📧 Owner has {len(notifications)} unread notifications")

    # Get stats
    stats = registry.get_stats()
    print(f"\n📊 Registry Stats:")
    print(f"   Total Owners: {stats['total_owners']}")
    print(f"   Agents by Status: {stats['agents_by_status']}")
    print(f"   Average Safety Rating: {stats['avg_safety_rating']:.1f}/5")
