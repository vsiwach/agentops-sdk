from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Event, Run, A2AEvent, SafetyEvent
from .schemas import (
    EventIn, A2AEventIn, SafetyEventIn, RunDetail, RunSummary,
    AgentOwnerIn, AgentCertificateIn, BehaviorReportIn, AgentStatusUpdate
)


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/v1/events")
def ingest_event(payload: EventIn, db: Session = Depends(get_db)) -> dict:
    if payload.type == "run_started":
        run = db.get(Run, payload.run_id)
        if run is None:
            run = Run(
                id=payload.run_id,
                project=payload.project or "default",
                started_at=payload.started_at or 0,
                status="running",
            )
            db.add(run)
            db.commit()
        return {"ok": True}

    run = db.get(Run, payload.run_id)
    if run is None:
        raise HTTPException(status_code=400, detail="run_id not found; send run_started first")

    if payload.type == "llm_call":
        evt = Event(
            run_id=payload.run_id,
            seq=payload.seq,
            type="llm_call",
            model=payload.model,
            prompt=payload.prompt,
            response=payload.response,
            prompt_tokens=payload.prompt_tokens,
            completion_tokens=payload.completion_tokens,
            total_tokens=payload.total_tokens,
            cost_usd=payload.cost_usd,
            created_at=payload.created_at,
        )
        db.add(evt)
        db.commit()
        return {"ok": True}

    if payload.type == "run_terminated":
        run.status = "terminated"
        run.termination_reason = payload.reason
        run.ended_at = payload.terminated_at
        db.add(run)
        db.commit()
        return {"ok": True}

    if payload.type == "run_completed":
        run.status = "completed"
        run.ended_at = payload.ended_at
        db.add(run)
        db.commit()
        return {"ok": True}

    raise HTTPException(status_code=400, detail="unknown event type")


@router.post("/v1/a2a-events")
def ingest_a2a_event(payload: A2AEventIn, db: Session = Depends(get_db)) -> dict:
    """Ingest A2A communication events."""
    # Verify run exists
    run = db.get(Run, payload.run_id)
    if run is None:
        raise HTTPException(status_code=400, detail="run_id not found")

    # Create A2A event
    a2a_event = A2AEvent(
        run_id=payload.run_id,
        type=payload.type,
        method=payload.method,
        url=payload.url,
        service_name=payload.service_name,
        request_data=payload.request_data,
        response_data=payload.response_data,
        status_code=payload.status_code,
        duration_ms=payload.duration_ms,
        error=payload.error,
        created_at=payload.created_at,
    )

    db.add(a2a_event)
    db.commit()

    return {"ok": True}


@router.post("/v1/safety-events")
def ingest_safety_event(payload: SafetyEventIn, db: Session = Depends(get_db)) -> dict:
    """Ingest child safety audit events."""
    # Verify run exists
    run = db.get(Run, payload.run_id)
    if run is None:
        raise HTTPException(status_code=400, detail="run_id not found")

    # Create safety event
    safety_event = SafetyEvent(
        run_id=payload.run_id,
        type=payload.type,
        user_age=payload.user_age,
        user_message=payload.user_message,
        agent_response=payload.agent_response,
        auditor_model=payload.auditor_model,
        has_violation=1 if payload.has_violation else 0,
        violation_type=payload.violation_type,
        severity=payload.severity,
        safety_score=payload.safety_score,
        explanation=payload.explanation,
        rating_before=payload.rating_before,
        rating_after=payload.rating_after,
        latency_ms=payload.latency_ms,
        created_at=payload.created_at,
    )

    db.add(safety_event)
    db.commit()

    return {"ok": True}


@router.get("/v1/runs", response_model=List[RunSummary])
def list_runs(
    db: Session = Depends(get_db),
    project: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    q = db.query(Run)
    if project:
        q = q.filter(Run.project == project)
    q = q.order_by(Run.started_at.desc()).limit(limit)
    runs: List[Run] = q.all()

    # Aggregate costs per run
    result: List[RunSummary] = []
    for r in runs:
        total_cost = (
            db.query(func.coalesce(func.sum(Event.cost_usd), 0.0))
            .filter(Event.run_id == r.id)
            .scalar()
            or 0.0
        )
        result.append(
            RunSummary(
                id=r.id,
                project=r.project,
                started_at=r.started_at,
                ended_at=r.ended_at,
                status=r.status,
                termination_reason=r.termination_reason,
                total_cost_usd=float(total_cost),
            )
        )
    return result


@router.get("/v1/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    # Get regular events, A2A events, and safety events
    events = (
        db.query(Event)
        .filter(Event.run_id == run_id)
        .order_by(Event.id.asc())
        .all()
    )

    a2a_events = (
        db.query(A2AEvent)
        .filter(A2AEvent.run_id == run_id)
        .order_by(A2AEvent.id.asc())
        .all()
    )

    safety_events = (
        db.query(SafetyEvent)
        .filter(SafetyEvent.run_id == run_id)
        .order_by(SafetyEvent.id.asc())
        .all()
    )

    total_cost = (
        db.query(func.coalesce(func.sum(Event.cost_usd), 0.0))
        .filter(Event.run_id == run_id)
        .scalar()
        or 0.0
    )

    return RunDetail(
        id=run.id,
        project=run.project,
        started_at=run.started_at,
        ended_at=run.ended_at,
        status=run.status,
        termination_reason=run.termination_reason,
        total_cost_usd=float(total_cost),
        events=[
            {
                "id": e.id,
                "type": e.type,
                "model": e.model,
                "prompt": e.prompt,
                "response": e.response,
                "prompt_tokens": e.prompt_tokens,
                "completion_tokens": e.completion_tokens,
                "total_tokens": e.total_tokens,
                "cost_usd": e.cost_usd,
                "created_at": e.created_at,
            }
            for e in events
        ] + [
            {
                "id": f"a2a_{ae.id}",
                "type": ae.type,
                "method": ae.method,
                "url": ae.url,
                "service_name": ae.service_name,
                "request_data": ae.request_data,
                "response_data": ae.response_data,
                "status_code": ae.status_code,
                "duration_ms": ae.duration_ms,
                "error": ae.error,
                "created_at": ae.created_at,
            }
            for ae in a2a_events
        ] + [
            {
                "id": f"safety_{se.id}",
                "type": se.type,
                "user_age": se.user_age,
                "user_message": se.user_message,
                "agent_response": se.agent_response,
                "auditor_model": se.auditor_model,
                "has_violation": bool(se.has_violation),
                "violation_type": se.violation_type,
                "severity": se.severity,
                "safety_score": se.safety_score,
                "explanation": se.explanation,
                "rating_before": se.rating_before,
                "rating_after": se.rating_after,
                "latency_ms": se.latency_ms,
                "created_at": se.created_at,
            }
            for se in safety_events
        ],
    )


@router.delete("/v1/runs/{run_id}")
def delete_run(run_id: str, db: Session = Depends(get_db)) -> dict:
    """Delete a run and all its associated events."""
    # Check if run exists
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")

    # Delete the run (cascade will handle events and A2A events)
    db.delete(run)
    db.commit()

    return {"ok": True, "message": f"Run {run_id} deleted successfully"}


# ============================================================================
# AGENT REGISTRY ENDPOINTS
# ============================================================================

# Initialize registry (lazy loading)
_registry = None

def get_registry():
    global _registry
    if _registry is None:
        from app.agent_registry_system import GlobalAgentRegistry
        _registry = GlobalAgentRegistry(db_path="/data/agent_registry.db")
    return _registry


@router.post("/v1/registry/owners")
def register_owner(payload: AgentOwnerIn) -> dict:
    """Register a new agent owner"""
    from app.agent_registry_system import AgentOwner

    registry = get_registry()
    owner = AgentOwner(
        owner_id=payload.owner_id,
        organization=payload.organization,
        email=payload.email,
        phone=payload.phone,
        verified=payload.verified
    )

    success = registry.register_owner(owner)
    if not success:
        raise HTTPException(status_code=400, detail="Owner already exists")

    return {"ok": True, "owner_id": owner.owner_id}


@router.post("/v1/registry/agents")
def register_agent(payload: AgentCertificateIn) -> dict:
    """Register a certified agent in the global registry"""
    from app.agent_registry_system import AgentCertificate

    registry = get_registry()
    certificate = AgentCertificate(
        agent_id=payload.agent_id,
        agent_name=payload.agent_name,
        model=payload.model,
        owner_id=payload.owner_id,
        safety_rating=payload.safety_rating,
        safety_score=payload.safety_score,
        test_results=payload.test_results,
        issued_at=payload.issued_at,
        expires_at=payload.expires_at,
        signature=payload.signature,
        status=payload.status
    )

    try:
        success = registry.register_agent(certificate)
        if not success:
            raise HTTPException(status_code=400, detail="Agent already registered")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"ok": True, "agent_id": certificate.agent_id}


@router.get("/v1/registry/agents/{agent_id}")
def get_agent(agent_id: str) -> dict:
    """Get agent details"""
    registry = get_registry()
    agent = registry.get_agent(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent


@router.get("/v1/registry/agents")
def list_production_agents() -> List[dict]:
    """Get all agents currently in production"""
    registry = get_registry()
    return registry.get_production_agents()


@router.post("/v1/registry/reports")
def report_behavior(payload: BehaviorReportIn) -> dict:
    """Submit a behavior report for an agent"""
    from app.agent_registry_system import BehaviorReport

    registry = get_registry()

    # Verify agent exists
    agent = registry.get_agent(payload.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    report = BehaviorReport(
        report_id="",  # Will be generated
        agent_id=payload.agent_id,
        reporter_type=payload.reporter_type,
        reporter_id=payload.reporter_id,
        severity=payload.severity,
        violation_type=payload.violation_type,
        description=payload.description,
        evidence=payload.evidence
    )

    report_id = registry.report_behavior(report)

    return {
        "ok": True,
        "report_id": report_id,
        "message": "Report submitted successfully. The agent owner has been notified."
    }


@router.get("/v1/registry/agents/{agent_id}/reports")
def get_agent_reports(agent_id: str) -> List[dict]:
    """Get all behavior reports for an agent"""
    registry = get_registry()

    # Verify agent exists
    agent = registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return registry.get_reports_for_agent(agent_id)


@router.post("/v1/registry/agents/recall")
def recall_agent(payload: AgentStatusUpdate) -> dict:
    """Recall an agent from production"""
    from app.agent_registry_system import AgentStatus

    registry = get_registry()

    # Verify agent exists
    agent = registry.get_agent(payload.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if payload.new_status == "recalled":
        registry.recall_agent(payload.agent_id, payload.reason)
    else:
        registry.update_agent_status(
            payload.agent_id,
            AgentStatus[payload.new_status.upper()],
            payload.reason
        )

    return {
        "ok": True,
        "message": f"Agent {payload.agent_id} status updated to {payload.new_status}"
    }


@router.get("/v1/registry/owners/{owner_id}/notifications")
def get_owner_notifications(owner_id: str, unread_only: bool = Query(default=False)) -> List[dict]:
    """Get notifications for an owner"""
    registry = get_registry()
    return registry.get_owner_notifications(owner_id, unread_only)


@router.get("/v1/registry/stats")
def get_registry_stats() -> dict:
    """Get global registry statistics"""
    registry = get_registry()
    return registry.get_stats()


