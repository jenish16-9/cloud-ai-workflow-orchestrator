from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4
from pydantic import BaseModel, Field

def now() -> datetime:
    return datetime.now(timezone.utc)

class WorkflowStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"

class WorkflowCreate(BaseModel):
    repository: str = Field(min_length=1, description="owner/repository")
    branch: str = "main"
    commit_sha: str = "local-dev"
    event_name: str = "manual"
    goal: str | None = None
    input: dict[str, Any] = Field(default_factory=dict)

class Step(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    kind: str = "transform"
    requires_approval: bool = False
    config: dict[str, Any] = Field(default_factory=dict)

class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    template: str = "ci_cd"
    repository: str
    branch: str
    commit_sha: str
    event_name: str
    input: dict[str, Any]
    steps: list[Step]
    goal: str | None = None
    status: WorkflowStatus = WorkflowStatus.queued
    output: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=now)
    updated_at: datetime = Field(default_factory=now)

class Event(BaseModel):
    type: str
    message: str
    timestamp: datetime = Field(default_factory=now)

class GitHubWebhook(BaseModel):
    repository: str
    branch: str = "main"
    commit_sha: str
    event_name: str = "push"
    goal: str | None = None
