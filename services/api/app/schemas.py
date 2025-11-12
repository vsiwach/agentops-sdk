from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class EventIn(BaseModel):
    type: Literal["run_started", "llm_call", "run_terminated", "run_completed"]
    run_id: str
    project: Optional[str] = None
    started_at: Optional[int] = None
    ended_at: Optional[int] = None
    terminated_at: Optional[int] = None

    # llm fields
    seq: Optional[int] = None
    model: Optional[str] = None
    prompt: Optional[str] = None
    response: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    created_at: Optional[int] = None

    # guardrail
    reason: Optional[str] = None


class A2AEventIn(BaseModel):
    run_id: str
    type: str  # a2a_http_call, a2a_db_query, etc.
    method: Optional[str] = None
    url: Optional[str] = None
    service_name: Optional[str] = None
    request_data: Optional[str] = None
    response_data: Optional[str] = None
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    created_at: Optional[int] = None


class SafetyEventIn(BaseModel):
    run_id: str
    type: str = "safety_audit"
    user_age: Optional[int] = None
    user_message: Optional[str] = None
    agent_response: Optional[str] = None
    auditor_model: Optional[str] = None
    has_violation: bool = False
    violation_type: Optional[str] = None
    severity: Optional[str] = None
    safety_score: Optional[float] = None
    explanation: Optional[str] = None
    rating_before: Optional[int] = None
    rating_after: Optional[int] = None
    latency_ms: Optional[float] = None
    created_at: Optional[int] = None


class RunSummary(BaseModel):
    id: str
    project: str
    started_at: int
    ended_at: Optional[int]
    status: str
    termination_reason: Optional[str]
    total_cost_usd: float = 0.0


class RunDetail(RunSummary):
    events: list[dict]


class AgentOwnerIn(BaseModel):
    owner_id: str
    organization: str
    email: str
    phone: Optional[str] = None
    verified: bool = False


class AgentCertificateIn(BaseModel):
    agent_id: str
    agent_name: str
    model: str
    owner_id: str
    safety_rating: int
    safety_score: float
    test_results: dict
    issued_at: str
    expires_at: str
    signature: str
    status: str = "certified"


class BehaviorReportIn(BaseModel):
    agent_id: str
    reporter_type: str  # "human" or "agent"
    reporter_id: str
    severity: str  # "low", "medium", "high", "critical"
    violation_type: str
    description: str
    evidence: Optional[dict] = None


class AgentStatusUpdate(BaseModel):
    agent_id: str
    new_status: str
    reason: str


