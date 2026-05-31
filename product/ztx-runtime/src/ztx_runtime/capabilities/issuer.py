"""One-time capability issuer and verifier."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, Field

from ztx_runtime.protocol.envelope import ActionRequest, UCPEnvelope


class CapabilityState(StrEnum):
    """Capability lifecycle states."""

    ACTIVE = "active"
    CONSUMED = "consumed"
    REVOKED = "revoked"
    EXPIRED = "expired"


class CapabilityGrant(BaseModel):
    """Short-lived scoped grant for exactly one action."""

    id: str = Field(default_factory=lambda: f"cap_{secrets.token_urlsafe(18)}")
    agent_id: str
    action_type: str
    action_name: str
    resource: str = ""
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime
    state: CapabilityState = CapabilityState.ACTIVE
    single_use: bool = True

    def is_expired(self, now: datetime | None = None) -> bool:
        return (now or datetime.now(UTC)) >= self.expires_at

    def can_authorize(self, agent_id: str, action: ActionRequest) -> bool:
        """Return true only if this grant matches the requested action."""
        return (
            self.state == CapabilityState.ACTIVE
            and not self.is_expired()
            and self.agent_id == agent_id
            and self.action_type == action.type
            and self.action_name == action.name
            and (not self.resource or self.resource == action.resource)
        )


class CapabilityIssuer:
    """In-memory issuer for prototype and unit tests."""

    def __init__(self) -> None:
        self._grants: dict[str, CapabilityGrant] = {}

    def issue(self, envelope: UCPEnvelope, ttl_seconds: int = 60) -> CapabilityGrant:
        grant = CapabilityGrant(
            agent_id=envelope.agent.id,
            action_type=envelope.action.type,
            action_name=envelope.action.name,
            resource=envelope.action.resource,
            expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds),
        )
        self._grants[grant.id] = grant
        return grant

    def verify(self, grant_id: str, envelope: UCPEnvelope) -> bool:
        grant = self._grants.get(grant_id)
        if grant is None:
            return False
        if grant.is_expired():
            grant.state = CapabilityState.EXPIRED
            return False
        return grant.can_authorize(envelope.agent.id, envelope.action)

    def consume(self, grant_id: str) -> None:
        grant = self._grants[grant_id]
        if grant.single_use:
            grant.state = CapabilityState.CONSUMED

    def revoke(self, grant_id: str) -> None:
        self._grants[grant_id].state = CapabilityState.REVOKED
