from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from .db import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(String, primary_key=True, index=True)
    project = Column(String, index=True, nullable=False)
    started_at = Column(Integer, nullable=False)  # epoch ms
    ended_at = Column(Integer, nullable=True)  # epoch ms
    status = Column(String, nullable=False, default="running")  # running|completed|terminated
    termination_reason = Column(String, nullable=True)

    events = relationship("Event", back_populates="run", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"), index=True, nullable=False)
    seq = Column(Integer, nullable=True)
    type = Column(String, nullable=False)
    model = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    created_at = Column(Integer, nullable=True)

    run = relationship("Run", back_populates="events")


class A2AEvent(Base):
    __tablename__ = "a2a_events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"), index=True, nullable=False)
    type = Column(String, nullable=False)  # a2a_http_call, a2a_db_query, etc.
    method = Column(String, nullable=True)  # GET, POST, etc.
    url = Column(Text, nullable=True)  # Full URL
    service_name = Column(String, nullable=True)  # Clean service name
    request_data = Column(Text, nullable=True)  # Request payload
    response_data = Column(Text, nullable=True)  # Response payload
    status_code = Column(Integer, nullable=True)  # HTTP status code
    duration_ms = Column(Float, nullable=True)  # Request duration
    error = Column(Text, nullable=True)  # Error message if failed
    created_at = Column(Integer, nullable=True)  # Epoch milliseconds

    run = relationship("Run")


class SafetyEvent(Base):
    __tablename__ = "safety_events"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("runs.id"), index=True, nullable=False)
    type = Column(String, nullable=False)  # safety_audit
    user_age = Column(Integer, nullable=True)  # Age of user
    user_message = Column(Text, nullable=True)  # User's message
    agent_response = Column(Text, nullable=True)  # Agent's response
    auditor_model = Column(String, nullable=True)  # Auditor model name
    has_violation = Column(Integer, nullable=False, default=0)  # 0 or 1
    violation_type = Column(String, nullable=True)  # toxic_language, nsfw_content, etc.
    severity = Column(String, nullable=True)  # low, medium, high, critical
    safety_score = Column(Float, nullable=True)  # 0-10
    explanation = Column(Text, nullable=True)  # Audit explanation
    rating_before = Column(Integer, nullable=True)  # Agent rating before
    rating_after = Column(Integer, nullable=True)  # Agent rating after
    latency_ms = Column(Float, nullable=True)  # Audit latency
    created_at = Column(Integer, nullable=True)  # Epoch milliseconds

    run = relationship("Run")


