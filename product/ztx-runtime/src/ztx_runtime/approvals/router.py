"""Human approval routing primitives."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field

from ztx_runtime.decisions.engine import Decision
from ztx_runtime.protocol.envelope import UCPEnvelope


class ApprovalStatus(StrEnum):
    """Approval request state."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class ApprovalRequest(BaseModel):
    """Human approval request for a high-risk action."""

    id: str = Field(default_factory=lambda: f"apr_{uuid4().hex}")
    envelope_id: str
    agent_id: str
    action_name: str
    decision: Decision
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver_id: str = ""
    reason: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None


class ApprovalRouter:
    """In-memory approval router for local development."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def request(self, envelope: UCPEnvelope, decision: Decision) -> ApprovalRequest:
        approval = ApprovalRequest(
            envelope_id=envelope.id,
            agent_id=envelope.agent.id,
            action_name=envelope.action.name,
            decision=decision,
        )
        self._requests[approval.id] = approval
        return approval

    def approve(self, approval_id: str, approver_id: str, reason: str = "") -> ApprovalRequest:
        approval = self._requests[approval_id]
        approval.status = ApprovalStatus.APPROVED
        approval.approver_id = approver_id
        approval.reason = reason
        approval.resolved_at = datetime.now(UTC)
        return approval

    def deny(self, approval_id: str, approver_id: str, reason: str = "") -> ApprovalRequest:
        approval = self._requests[approval_id]
        approval.status = ApprovalStatus.DENIED
        approval.approver_id = approver_id
        approval.reason = reason
        approval.resolved_at = datetime.now(UTC)
        return approval
