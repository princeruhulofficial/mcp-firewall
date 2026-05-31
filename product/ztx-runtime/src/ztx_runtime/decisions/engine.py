"""Deterministic decision engine v1."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from ztx_runtime.protocol.envelope import ActionEffect, Sensitivity, UCPEnvelope


class DecisionOutcome(StrEnum):
    """Possible pre-execution outcomes."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    ISSUE_CAPABILITY = "issue_capability"
    SANDBOX = "sandbox"
    MONITOR_ONLY = "monitor_only"


class RiskLevel(StrEnum):
    """Risk bands used by the decision engine."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessment(BaseModel):
    """Explainable risk score."""

    score: int = Field(ge=0, le=100)
    level: RiskLevel
    factors: list[str] = Field(default_factory=list)


class Decision(BaseModel):
    """Decision returned before action execution."""

    outcome: DecisionOutcome
    reason_code: str
    reason: str
    risk: RiskAssessment


class DecisionEngine:
    """Small deterministic policy/risk engine for the first runtime."""

    def evaluate(self, envelope: UCPEnvelope) -> Decision:
        """Evaluate an action envelope before execution."""
        risk = self._score(envelope)

        if risk.score >= 90:
            return Decision(
                outcome=DecisionOutcome.DENY,
                reason_code="critical_risk_denied",
                reason="Critical-risk action is denied by default.",
                risk=risk,
            )
        if risk.score >= 70:
            return Decision(
                outcome=DecisionOutcome.REQUIRE_APPROVAL,
                reason_code="human_approval_required",
                reason="High-risk action requires human approval.",
                risk=risk,
            )
        if risk.score >= 35:
            return Decision(
                outcome=DecisionOutcome.ISSUE_CAPABILITY,
                reason_code="capability_required",
                reason="Medium-risk action requires a scoped capability.",
                risk=risk,
            )
        return Decision(
            outcome=DecisionOutcome.ALLOW,
            reason_code="low_risk_allowed",
            reason="Low-risk action can proceed with audit.",
            risk=risk,
        )

    def _score(self, envelope: UCPEnvelope) -> RiskAssessment:
        score = 0
        factors: list[str] = []
        effects = set(envelope.action.expected_effects)

        if ActionEffect.READ in effects:
            score += 5
            factors.append("reads data")
        if ActionEffect.WRITE in effects:
            score += 25
            factors.append("changes state")
        if ActionEffect.NETWORK in effects:
            score += 25
            factors.append("uses network")
        if ActionEffect.EXECUTE in effects:
            score += 35
            factors.append("executes code or commands")
        if ActionEffect.ADMIN in effects:
            score += 45
            factors.append("admin-level action")
        if ActionEffect.PAYMENT in effects:
            score += 50
            factors.append("payment-related action")

        if any(record.sensitivity == Sensitivity.RESTRICTED for record in envelope.active_contexts()):
            score += 30
            factors.append("restricted context present")
        elif any(record.sensitivity == Sensitivity.CONFIDENTIAL for record in envelope.active_contexts()):
            score += 15
            factors.append("confidential context present")

        score = min(score, 100)
        if score >= 90:
            level = RiskLevel.CRITICAL
        elif score >= 70:
            level = RiskLevel.HIGH
        elif score >= 35:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return RiskAssessment(score=score, level=level, factors=factors)
