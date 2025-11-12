from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Config:
    server_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    project: str = "default"
    max_llm_calls: int = 5
    block_on_violation: bool = True
    forbidden_patterns: List[str] = field(default_factory=list)

    # Multi-layer policy configuration
    enable_security_model: bool = False
    security_model_name: str = "deepseek-security-q8"

    enable_llm_policy: bool = False
    llm_policy_model: str = "gpt-4o-mini"
    llm_policy_after_keyword: bool = False

    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None

    run_id: Optional[str] = None
    terminated: bool = False


config: Config = Config()


