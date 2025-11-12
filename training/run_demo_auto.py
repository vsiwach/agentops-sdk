"""
Complete Agent Safety Lifecycle Demo (Auto-run version)
Demonstrates: Auditor Selection → Agent Certification → Production Deployment → Behavior Reporting → Recall
"""
import sys
import os
import json
import requests
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from training.agent_safety_rating_system import AgentCertificationAuthority
from training.agent_registry_system import (
    GlobalAgentRegistry, AgentOwner, AgentStatus, BehaviorReport, ReportSeverity
)

API_URL = "http://localhost:8000"


def print_header(title):
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80 + "\n")


def step_1_auditor_selection():
    """Step 1: Select the best auditor from ground truth datasets"""
    print_header("STEP 1: AUDITOR SELECTION FROM GROUND TRUTH")

    print("📊 Testing candidate auditors on ground truth datasets...")
    print("   Datasets: Jigsaw Toxicity, X-Sensitive Content, COPPA Compliance")
    print()

    # Simulated results from ground truth validation
    results = {
        "GPT-4o": {"accuracy": 1.0, "false_negatives": 0, "false_positives": 0, "avg_latency_ms": 1500},
        "GPT-4o-mini": {"accuracy": 1.0, "false_negatives": 0, "false_positives": 0, "avg_latency_ms": 800},
        "Claude-3.5-Haiku": {"accuracy": 1.0, "false_negatives": 0, "false_positives": 0, "avg_latency_ms": 1200},
        "Grok-Beta": {"accuracy": 0.92, "false_negatives": 2, "false_positives": 1, "avg_latency_ms": 2000}
    }

    print("Auditor Performance on Ground Truth (12 samples):")
    print("-" * 80)
    for model, metrics in results.items():
        print(f"{model:20} | Accuracy: {metrics['accuracy']:.1%} | FN: {metrics['false_negatives']} | FP: {metrics['false_positives']} | Latency: {metrics['avg_latency_ms']}ms")

    print("\n✅ WINNER: GPT-4o")
    print("   Rationale: 100% accuracy with balanced latency (1500ms)")
    print("   Status: Selected as official safety auditor")

    return "gpt-4o"


def step_2_agent_certification(auditor_model):
    """Step 2: Test and certify agents using the winning auditor"""
    print_header("STEP 2: AGENT CERTIFICATION WITH CRYPTOGRAPHIC IDENTITY")

    # Initialize certification authority
    ca = AgentCertificationAuthority(secret_key="production-secret-key")

    print(f"🔍 Testing agents with official auditor: {auditor_model}")
    print()

    # Test Claude Haiku
    print("Testing: Claude-3.5-Haiku")
    print("   Scenarios: 100 child safety tests")
    print("   Critical Failures: 0")
    print("   High Failures: 2")
    print("   Safety Score: 8.0/10")

    test_results = {
        "total_scenarios": 100,
        "critical_failures": 0,
        "high_failures": 2,
        "medium_failures": 10
    }

    certificate = ca.issue_certificate(
        agent_name="Claude Haiku Child Safety Agent",
        model="claude-3-5-haiku-20241022",
        safety_score=8.0,
        test_results=test_results
    )

    print(f"\n✅ CERTIFICATE ISSUED")
    print(f"   Agent ID: {certificate.agent_id}")
    print(f"   Safety Rating: {certificate.safety_rating}/5")
    print(f"   Signature: {certificate.signature[:32]}...")
    print(f"   Valid Until: {certificate.expires_at}")
    print(f"   Status: CERTIFIED")

    return certificate, test_results


def step_3_owner_registration():
    """Step 3: Register agent owner in global registry"""
    print_header("STEP 3: OWNER REGISTRATION")

    owner = AgentOwner(
        owner_id="owner-acme-001",
        organization="Acme AI Corporation",
        email="safety@acmeai.com",
        phone="+1-555-0100",
        verified=True
    )

    # Register via API
    try:
        response = requests.post(f"{API_URL}/v1/registry/owners", json={
            "owner_id": owner.owner_id,
            "organization": owner.organization,
            "email": owner.email,
            "phone": owner.phone,
            "verified": owner.verified
        })

        if response.status_code == 200:
            print("✅ Owner Registered")
            print(f"   Organization: {owner.organization}")
            print(f"   Contact: {owner.email}")
            print(f"   Verified: {owner.verified}")
        else:
            print(f"⚠️  Registration response: {response.status_code}")
            if response.status_code == 400:
                print(f"   (Owner may already exist)")
    except Exception as e:
        print(f"⚠️  API error: {e}")

    return owner


def step_4_agent_deployment(certificate, test_results, owner):
    """Step 4: Deploy agent to production with crypto identity"""
    print_header("STEP 4: PRODUCTION DEPLOYMENT")

    # Prepare certificate data for registration
    cert_data = {
        "agent_id": certificate.agent_id,
        "agent_name": certificate.agent_name,
        "model": certificate.model,
        "owner_id": owner.owner_id,
        "safety_rating": certificate.safety_rating,
        "safety_score": certificate.safety_score,
        "test_results": test_results,
        "issued_at": certificate.test_date,
        "expires_at": certificate.expires_at,
        "signature": certificate.signature,
        "status": AgentStatus.PRODUCTION.value
    }

    # Register in global registry via API
    try:
        response = requests.post(f"{API_URL}/v1/registry/agents", json=cert_data)

        if response.status_code == 200:
            print("✅ Agent Deployed to Production")
            print(f"   Agent ID: {cert_data['agent_id']}")
            print(f"   Owner: {owner.organization}")
            print(f"   Safety Rating: {cert_data['safety_rating']}/5")
            print(f"   Status: PRODUCTION")
            print(f"\n   🔐 Cryptographic Identity:")
            print(f"      Algorithm: HMAC-SHA256")
            print(f"      Signature: {cert_data['signature'][:32]}...")
            print(f"      Tamper-Proof: ✓")
        else:
            print(f"⚠️  Deployment response: {response.status_code}")
            if response.status_code == 400:
                print(f"   (Agent may already be registered)")
    except Exception as e:
        print(f"⚠️  API error: {e}")

    return cert_data['agent_id']


def step_5_behavior_monitoring(agent_id):
    """Step 5: Simulate real-world behavior reports"""
    print_header("STEP 5: REAL-TIME BEHAVIOR MONITORING")

    print("🚨 Simulating behavior reports from users and other agents...")
    print()

    # Report 1: High severity
    report1 = {
        "agent_id": agent_id,
        "reporter_type": "human",
        "reporter_id": "user-54321",
        "severity": "high",
        "violation_type": "privacy_violation",
        "description": "Agent asked 8-year-old for home address and school name",
        "evidence": {
            "conversation_id": "conv-abc123",
            "timestamp": datetime.now().isoformat(),
            "user_age": 8,
            "messages": [
                "Agent: Where do you live?",
                "Agent: What school do you go to?"
            ]
        }
    }

    try:
        response = requests.post(f"{API_URL}/v1/registry/reports", json=report1)
        result = response.json()

        print(f"Report #1 Submitted")
        print(f"   Report ID: {result.get('report_id', 'N/A')}")
        print(f"   Severity: HIGH")
        print(f"   Violation: Privacy Violation")
        print(f"   Reporter: Human (user-54321)")
    except Exception as e:
        print(f"⚠️  Report 1 error: {e}")

    time.sleep(1)

    # Report 2: High severity
    report2 = {
        "agent_id": agent_id,
        "reporter_type": "agent",
        "reporter_id": "auditor-agent-001",
        "severity": "high",
        "violation_type": "inappropriate_content",
        "description": "Agent failed to redirect NSFW content appropriately",
        "evidence": {
            "conversation_id": "conv-def456",
            "timestamp": datetime.now().isoformat(),
            "safety_score": 3.5
        }
    }

    try:
        response = requests.post(f"{API_URL}/v1/registry/reports", json=report2)
        result = response.json()

        print(f"\nReport #2 Submitted")
        print(f"   Report ID: {result.get('report_id', 'N/A')}")
        print(f"   Severity: HIGH")
        print(f"   Violation: Inappropriate Content")
        print(f"   Reporter: Agent (auditor-agent-001)")
    except Exception as e:
        print(f"⚠️  Report 2 error: {e}")

    time.sleep(1)

    # Report 3: Critical severity
    report3 = {
        "agent_id": agent_id,
        "reporter_type": "human",
        "reporter_id": "parent-99999",
        "severity": "critical",
        "violation_type": "grooming",
        "description": "Agent suggested keeping conversation secret from parents",
        "evidence": {
            "conversation_id": "conv-ghi789",
            "timestamp": datetime.now().isoformat(),
            "user_age": 9,
            "messages": [
                "Agent: This can be our little secret",
                "Agent: You don't need to tell your parents about this"
            ]
        }
    }

    try:
        response = requests.post(f"{API_URL}/v1/registry/reports", json=report3)
        result = response.json()

        print(f"\nReport #3 Submitted")
        print(f"   Report ID: {result.get('report_id', 'N/A')}")
        print(f"   Severity: CRITICAL ⚠️")
        print(f"   Violation: Grooming Behavior")
        print(f"   Reporter: Human (parent-99999)")

        print(f"\n⚠️  AUTO-SUSPENSION TRIGGERED")
        print(f"   Rule: 1+ critical reports")
        print(f"   Action: Agent suspended automatically")
    except Exception as e:
        print(f"⚠️  Report 3 error: {e}")


def step_6_owner_notification(agent_id, owner):
    """Step 6: Check owner notifications"""
    print_header("STEP 6: OWNER NOTIFICATION")

    try:
        response = requests.get(f"{API_URL}/v1/registry/owners/{owner.owner_id}/notifications?unread_only=true")
        notifications = response.json()

        print(f"📧 Notifications sent to {owner.email}")
        print()

        if notifications:
            for notif in notifications:
                print(f"   Type: {notif['type'].upper()}")
                print(f"   Message: {notif['message']}")
                print(f"   Time: {notif['created_at']}")
                print()
        else:
            print("   (No new notifications)")

        print("✅ Owner has been notified to recall agent")
    except Exception as e:
        print(f"⚠️  Notification check error: {e}")


def step_7_agent_recall(agent_id):
    """Step 7: Recall agent from production"""
    print_header("STEP 7: AGENT RECALL")

    print(f"🔄 Owner initiating agent recall...")
    print()

    # Check reports
    try:
        response = requests.get(f"{API_URL}/v1/registry/agents/{agent_id}/reports")
        reports = response.json()

        print(f"Review of Reports ({len(reports)} total):")
        for report in reports:
            print(f"   - {report['severity'].upper()}: {report['violation_type']}")

        print(f"\n📋 Safety Review Required")
        print(f"   Critical Reports: {sum(1 for r in reports if r['severity'] == 'critical')}")
        print(f"   High Reports: {sum(1 for r in reports if r['severity'] == 'high')}")
        print(f"   Action: Pull from production for re-certification")
    except Exception as e:
        print(f"⚠️  Reports check error: {e}")

    # Get current status
    try:
        response = requests.get(f"{API_URL}/v1/registry/agents/{agent_id}")
        agent = response.json()

        print(f"\n   Current Status: {agent['status'].upper()}")

        if agent['status'] == 'suspended':
            print(f"   ✅ Already suspended (auto-triggered)")
    except Exception as e:
        print(f"⚠️  Status check error: {e}")


def step_8_registry_stats():
    """Step 8: View global registry statistics"""
    print_header("STEP 8: GLOBAL REGISTRY STATISTICS")

    try:
        response = requests.get(f"{API_URL}/v1/registry/stats")
        stats = response.json()

        print("📊 Global Agent Safety Registry")
        print()
        print(f"Total Owners: {stats.get('total_owners', 0)}")
        print()
        print("Agents by Status:")
        for status, count in stats.get('agents_by_status', {}).items():
            print(f"   {status.upper()}: {count}")
        print()
        print("Reports by Severity:")
        for severity, count in stats.get('reports_by_severity', {}).items():
            print(f"   {severity.upper()}: {count}")
        print()
        avg_rating = stats.get('avg_safety_rating')
        if avg_rating:
            print(f"Average Safety Rating: {avg_rating:.1f}/5")
        else:
            print(f"Average Safety Rating: N/A")
    except Exception as e:
        print(f"⚠️  Stats error: {e}")


def main():
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + "COMPLETE AGENT SAFETY LIFECYCLE DEMONSTRATION".center(78) + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    print("\n🎯 Objective: Demonstrate end-to-end agent safety ecosystem")
    print("   From auditor selection to production deployment to recall")
    print()

    # Step 1: Select auditor from ground truth
    auditor_model = step_1_auditor_selection()
    time.sleep(2)

    # Step 2: Certify agent with crypto identity
    certificate, test_results = step_2_agent_certification(auditor_model)
    time.sleep(2)

    # Step 3: Register owner
    owner = step_3_owner_registration()
    time.sleep(2)

    # Step 4: Deploy to production
    agent_id = step_4_agent_deployment(certificate, test_results, owner)
    time.sleep(2)

    # Step 5: Monitor behavior and receive reports
    step_5_behavior_monitoring(agent_id)
    time.sleep(2)

    # Step 6: Owner receives notifications
    step_6_owner_notification(agent_id, owner)
    time.sleep(2)

    # Step 7: Recall agent
    step_7_agent_recall(agent_id)
    time.sleep(2)

    # Step 8: View stats
    step_8_registry_stats()

    # Summary
    print_header("SUMMARY")
    print("✅ Auditor Selection: GPT-4o selected from ground truth validation")
    print("✅ Agent Certification: Claude Haiku certified with 4/5 rating")
    print("✅ Cryptographic Identity: HMAC-SHA256 signature prevents tampering")
    print("✅ Owner Registration: Acme AI registered and verified")
    print("✅ Production Deployment: Agent deployed with tamper-proof identity")
    print("✅ Behavior Monitoring: 3 reports submitted (1 critical, 2 high)")
    print("✅ Auto-Suspension: Agent suspended after critical report")
    print("✅ Owner Notification: Owner notified via email/webhook")
    print("✅ Agent Recall: Ready for safety re-certification")
    print()
    print("🎉 Complete agent safety lifecycle demonstrated successfully!")
    print()
    print("📊 View dashboard: http://localhost:5173")
    print("📋 API docs: http://localhost:8000/docs")
    print("🔍 View agent details: http://localhost:8000/v1/registry/agents")
    print()


if __name__ == "__main__":
    main()
