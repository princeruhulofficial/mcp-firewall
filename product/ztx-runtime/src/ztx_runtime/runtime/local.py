"""Local runtime orchestration."""

from __future__ import annotations

from pydantic import BaseModel

from ztx_runtime.approvals.router import ApprovalRequest, ApprovalRouter
from ztx_runtime.capabilities.issuer import CapabilityGrant, CapabilityIssuer
from ztx_runtime.decisions.engine import Decision, DecisionEngine, DecisionOutcome
from ztx_runtime.protocol.envelope import UCPEnvelope


class RuntimeResult(BaseModel):
    """Result of submitting an envelope to the local runtime."""

    decision: Decision
    capability: CapabilityGrant | None = None
    approval: ApprovalRequest | None = None


class LocalRuntime:
    """Small local Zero Trust runtime."""

    def __init__(self) -> None:
        self.decisions = DecisionEngine()
        self.capabilities = CapabilityIssuer()
        self.approvals = ApprovalRouter()

    def submit(self, envelope: UCPEnvelope) -> RuntimeResult:
        """Evaluate one action and return the required next step."""
        decision = self.decisions.evaluate(envelope)

        if decision.outcome == DecisionOutcome.ISSUE_CAPABILITY:
            capability = self.capabilities.issue(envelope)
            return RuntimeResult(decision=decision, capability=capability)

        if decision.outcome == DecisionOutcome.REQUIRE_APPROVAL:
            approval = self.approvals.request(envelope, decision)
            return RuntimeResult(decision=decision, approval=approval)

        return RuntimeResult(decision=decision)

    def execute_with_capability(self, envelope: UCPEnvelope, capability_id: str) -> bool:
        """Prototype execution gate: verify and consume a capability."""
        if not self.capabilities.verify(capability_id, envelope):
            return False
        self.capabilities.consume(capability_id)
        return True
