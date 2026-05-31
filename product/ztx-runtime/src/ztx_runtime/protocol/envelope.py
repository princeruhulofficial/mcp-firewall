"""Universal Context Protocol envelope models.

These models are a clean-room foundation for representing AI actions before
policy, risk, approval, and capability checks run.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ContextScope(StrEnum):
    """Portable context scopes carried across agents and adapters."""

    USER = "user"
    TASK = "task"
    MEMORY = "memory"
    TOOL = "tool"
    ENVIRONMENT = "environment"
    SESSION = "session"
    AGENT = "agent"


class Sensitivity(StrEnum):
    """Data sensitivity labels for context minimization and policy decisions."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ActionPhase(StrEnum):
    """Standard action lifecycle phases."""

    READ_CONTEXT = "read_context"
    PROPOSE_ACTION = "propose_action"
    VALIDATE_ACTION = "validate_action"
    AWAIT_APPROVAL = "await_approval"
    ISSUE_CAPABILITY = "issue_capability"
    EXECUTE_ACTION = "execute_action"
    COMPLETE_ACTION = "complete_action"
    REVOKE_CAPABILITY = "revoke_capability"
    RECORD_AUDIT = "record_audit"


class ActionEffect(StrEnum):
    """Expected effect categories for risk scoring."""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"
    ADMIN = "admin"
    PAYMENT = "payment"


class IdentityRef(BaseModel):
    """Small identity reference used for users, agents, tools, and models."""

    id: str
    kind: str
    display_name: str = ""


class ContextRecord(BaseModel):
    """Portable context record."""

    id: str = Field(default_factory=lambda: f"ctx_{uuid4().hex}")
    scope: ContextScope
    data: dict[str, Any] = Field(default_factory=dict)
    subject: str = ""
    sensitivity: Sensitivity = Sensitivity.INTERNAL
    source: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        """Return true when this context should no longer be used."""
        if self.expires_at is None:
            return False
        return (now or datetime.now(UTC)) >= self.expires_at


class ActionRequest(BaseModel):
    """Adapter-neutral action request."""

    type: str
    name: str
    adapter: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    resource: str = ""
    expected_effects: list[ActionEffect] = Field(default_factory=list)


class UCPEnvelope(BaseModel):
    """Envelope passed from adapters into the Zero Trust runtime."""

    model_config = ConfigDict(populate_by_name=True)

    schema_id: str = Field(default="ucp.envelope", alias="schema")
    version: int = 1
    id: str = Field(default_factory=lambda: f"ucp_{uuid4().hex}")
    phase: ActionPhase = ActionPhase.PROPOSE_ACTION
    organization_id: str = ""
    workspace_id: str = ""
    user: IdentityRef | None = None
    agent: IdentityRef
    model: IdentityRef | None = None
    session_id: str = Field(default_factory=lambda: f"sess_{uuid4().hex}")
    contexts: list[ContextRecord] = Field(default_factory=list)
    action: ActionRequest
    extensions: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def active_contexts(
        self,
        scope: ContextScope | None = None,
        now: datetime | None = None,
    ) -> list[ContextRecord]:
        """Return non-expired contexts, optionally filtered by scope."""
        records = [record for record in self.contexts if not record.is_expired(now)]
        if scope is None:
            return records
        return [record for record in records if record.scope == scope]

    def to_json(self) -> str:
        """Serialize the envelope to JSON."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, payload: str) -> "UCPEnvelope":
        """Deserialize an envelope from JSON."""
        return cls.model_validate_json(payload)
