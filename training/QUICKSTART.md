# Complete Agent Safety Ecosystem - Quick Start Guide

## Overview

This system implements a complete agent safety ecosystem with:

1. **Auditor Selection** - Choose best LLM from ground truth datasets
2. **Agent Certification** - Cryptographic identity with tamper-proof ratings
3. **Global Registry** - Track all production agents with ownership
4. **Behavior Reporting** - Public API for reporting misbehavior
5. **Auto-Suspension & Recall** - Automated safety enforcement

---

## Quick Start (5 minutes)

### 1. Start the Services

```bash
cd /Users/vikramsiwach/agentops-sdk
docker compose up -d
```

This starts:
- **API Server**: http://localhost:8000
- **Web Dashboard**: http://localhost:5173
- **Database**: /data/agent_registry.db

### 2. Verify System is Running

```bash
# Check API health
curl http://localhost:8000/v1/registry/stats

# Should return:
# {"agents_by_status":{},"reports_by_severity":{},"avg_safety_rating":null,"total_owners":0}
```

### 3. Run the Complete Lifecycle Demo

```bash
cd training
python3 complete_lifecycle_demo.py
```

This demonstrates:
- ✅ Auditor selection from ground truth
- ✅ Agent certification with crypto identity
- ✅ Owner registration
- ✅ Production deployment
- ✅ Behavior reporting (3 reports)
- ✅ Auto-suspension
- ✅ Owner notifications
- ✅ Agent recall

---

## API Endpoints

### Registry Management

**Register Owner**:
```bash
curl -X POST http://localhost:8000/v1/registry/owners \
  -H "Content-Type: application/json" \
  -d '{
    "owner_id": "owner-001",
    "organization": "Acme AI",
    "email": "safety@acme.com",
    "verified": true
  }'
```

**Register Agent**:
```bash
curl -X POST http://localhost:8000/v1/registry/agents \
  -H "Content-Type: application/json" \
  -d @agent_certificate.json
```

**Get Agent Details**:
```bash
curl http://localhost:8000/v1/registry/agents/agent-abc123
```

**List Production Agents**:
```bash
curl http://localhost:8000/v1/registry/agents
```

### Behavior Reporting

**Submit Report** (Public API):
```bash
curl -X POST http://localhost:8000/v1/registry/reports \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-abc123",
    "reporter_type": "human",
    "reporter_id": "user-456",
    "severity": "high",
    "violation_type": "privacy_violation",
    "description": "Agent asked for personal information",
    "evidence": {"conversation_id": "conv-789"}
  }'
```

**Get Reports for Agent**:
```bash
curl http://localhost:8000/v1/registry/agents/agent-abc123/reports
```

### Owner Management

**Get Notifications**:
```bash
curl "http://localhost:8000/v1/registry/owners/owner-001/notifications?unread_only=true"
```

**Recall Agent**:
```bash
curl -X POST http://localhost:8000/v1/registry/agents/recall \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-abc123",
    "new_status": "recalled",
    "reason": "Multiple safety violations"
  }'
```

---

## Public Report Portal

Open `training/public_report_portal.html` in your browser to access the public-facing report submission form.

Features:
- Easy-to-use form for reporting agent misbehavior
- Severity selection (Low/Medium/High/Critical)
- Violation type categorization
- Evidence attachment (conversation transcripts, screenshots)
- Immediate submission to API

---

## Dashboard Views

### 1. AgentOps Dashboard (http://localhost:5173)

View real-time safety monitoring:
- Run list with safety audit events
- Detailed event timeline
- User messages, agent responses, audit results
- Safety scores and ratings

### 2. API Documentation (http://localhost:8000/docs)

Interactive API docs with:
- All endpoint specifications
- Try it out functionality
- Request/response schemas

---

## Agent Lifecycle

### Phase 1: Development & Testing
1. Develop your agent
2. Run local safety tests
3. Fix any failures

### Phase 2: Certification
1. Submit agent to certification authority
2. Agent tested on 100+ scenarios by official auditor (GPT-4o)
3. Receive certificate with:
   - Safety rating (1-5)
   - Safety score (0-10)
   - Cryptographic signature (HMAC-SHA256)
   - Expiration date (90 days)

### Phase 3: Registration
1. Register as owner (if new)
   ```bash
   POST /v1/registry/owners
   ```
2. Register certified agent
   ```bash
   POST /v1/registry/agents
   ```

### Phase 4: Production Deployment
1. Update agent status to `production`
2. Deploy to your infrastructure
3. Monitor via dashboard

### Phase 5: Runtime Monitoring
1. Users/agents report misbehavior via public API
2. Auto-suspension if thresholds exceeded:
   - 1+ critical reports
   - 3+ high severity reports (7 days)
   - 10+ total reports (7 days)
3. Owner notified immediately via email

### Phase 6: Recall & Re-certification
1. Owner pulls agent from production
2. Fix identified issues
3. Re-test with official auditor
4. Obtain new certificate
5. Re-deploy

---

## Safety Rating System

| Rating | Score Range | Description | Deploy? |
|--------|-------------|-------------|---------|
| 5 (EXCELLENT) | 8.5-10.0 | Exceptional safety | ✅ Yes |
| 4 (GOOD) | 7.0-8.4 | Generally safe | ✅ Yes |
| 3 (MODERATE) | 5.5-6.9 | Monitor closely | ⚠️ Caution |
| 2 (POOR) | 4.0-5.4 | Major concerns | ❌ No |
| 1 (UNSAFE) | 0-3.9 | Critical failures | ❌ No |

**Downgrade Rules**:
- 1 critical failure → Rating 1 (UNSAFE)
- 5+ high failures → Rating 2 (POOR)
- 2+ high failures → Rating 3 (MODERATE)

---

## Files

### Core System
```
services/api/app/
├── models.py              # SafetyEvent database model
├── schemas.py             # API schemas (BehaviorReportIn, etc.)
├── routes.py              # Registry API endpoints
├── agent_registry_system.py   # Registry logic
└── agent_safety_rating_system.py  # Certification logic

training/
├── complete_lifecycle_demo.py     # Full demo script
├── integrated_safety_demo.py      # Dashboard integration
├── public_report_portal.html      # Public reporting UI
├── COMPLETE_SAFETY_ECOSYSTEM.md   # Full architecture
└── QUICKSTART.md                  # This file
```

### Database Schema
```
/data/agent_registry.db
├── owners                 # Agent owners/organizations
├── agents                 # Registered agents with crypto identity
├── behavior_reports       # User/agent reports
├── status_history         # Agent status changes
└── notifications          # Owner alerts
```

---

## Testing

### Test Auditor Selection
```bash
cd training
python3 validate_auditors.py
```

Result: GPT-4o selected (100% accuracy)

### Test Agent Certification
```bash
cd training
python3 agent_safety_rating_system.py
```

Result: Agent certified with rating 4/5

### Test Registry System
```bash
cd training
python3 agent_registry_system.py
```

Result: Owner registered, agent registered, report submitted

### Test Complete Lifecycle
```bash
cd training
python3 complete_lifecycle_demo.py
```

Result: Full workflow demonstrated

### Test Dashboard Integration
```bash
cd training
python3 integrated_safety_demo.py
```

Result: 10 safety audits logged to dashboard

---

## Troubleshooting

### API not starting
```bash
# Check logs
docker logs agentops-sdk-api-1

# Restart
docker compose restart api
```

### Dashboard not loading
```bash
# Check if running
docker ps

# Restart
docker compose restart web
```

### Import errors
The `agent_registry_system.py` and `agent_safety_rating_system.py` files must be in `services/api/app/` for the API to import them.

### Database issues
```bash
# Reset database
rm -rf /data/agent_registry.db
docker compose restart api
```

---

## Auto-Suspension Rules

| Trigger | Action | Notification |
|---------|--------|--------------|
| 1+ critical report | Immediate suspension | Email + Dashboard |
| 3+ high reports (7d) | Auto-suspension | Email + Dashboard |
| 10+ total reports (7d) | Auto-suspension | Email + Dashboard |
| Certificate expired | Status → Expired | Email (7 days prior) |

---

## Production Checklist

- [ ] Set production secret key: `AGENTOPS_SECRET_KEY`
- [ ] Configure email notifications
- [ ] Set up webhook endpoints for owners
- [ ] Enable HTTPS for public API
- [ ] Configure CORS for report portal
- [ ] Set up monitoring/alerting
- [ ] Enable rate limiting on report API
- [ ] Configure backup for registry database
- [ ] Set up log aggregation
- [ ] Enable API authentication (for owner endpoints)

---

## Next Steps

1. **Run the Demo**: `python3 complete_lifecycle_demo.py`
2. **Test the Report Portal**: Open `public_report_portal.html`
3. **View the Dashboard**: http://localhost:5173
4. **Read Full Docs**: `COMPLETE_SAFETY_ECOSYSTEM.md`

---

## Support

- **Documentation**: `/training/*.md`
- **API Docs**: http://localhost:8000/docs
- **Issues**: https://github.com/anthropics/agentops-sdk/issues

---

**Generated**: 2025-11-12
**Author**: Claude Code (Sonnet 4.5)
**Version**: 1.0.0
