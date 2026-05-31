"""Tests for Zero Trust AI Execution Layer primitives."""

from __future__ import annotations

import time

from mcp_firewall.models import (
    CapabilityGrant,
    CapabilityStatus,
    ContextRecord,
    ContextScope,
    RiskAssessment,
    Severity,
    ToolCallRequest,
    UCPEnvelope,
)


class TestRiskAssessment:
    def test_score_bands(self):
        assert RiskAssessment.from_score(0).severity == Severity.INFO
        assert RiskAssessment.from_score(10).severity == Severity.LOW
        assert RiskAssessment.from_score(40).severity == Severity.MEDIUM
        assert RiskAssessment.from_score(70).severity == Severity.HIGH
        assert RiskAssessment.from_score(90).severity == Severity.CRITICAL

    def test_high_risk_requires_approval(self):
        assessment = RiskAssessment.from_score(75, factors=["production write"])

        assert assessment.requires_approval
        assert assessment.factors == ["production write"]

    def test_medium_risk_does_not_require_approval_by_default(self):
        assessment = RiskAssessment.from_score(55)

        assert not assessment.requires_approval


class TestCapabilityGrant:
    def test_new_capability_is_usable(self):
        grant = CapabilityGrant(agent_id="agent-1", tool_name="github.create_pr")

        assert grant.id.startswith("cap_")
        assert grant.status == CapabilityStatus.ACTIVE
        assert grant.usable

    def test_single_use_capability_is_consumed(self):
        grant = CapabilityGrant(agent_id="agent-1", tool_name="github.create_pr")

        grant.consume()

        assert grant.status == CapabilityStatus.CONSUMED
        assert not grant.usable

    def test_capability_can_be_revoked(self):
        grant = CapabilityGrant(agent_id="agent-1", tool_name="github.create_pr")

        grant.revoke()

        assert grant.status == CapabilityStatus.REVOKED
        assert not grant.usable

    def test_expired_capability_is_not_usable(self):
        grant = CapabilityGrant(
            agent_id="agent-1",
            tool_name="github.create_pr",
            expires_at=time.time() - 1,
        )

        assert grant.expired
        assert not grant.usable


class TestUniversalContextProtocol:
    def test_context_record_expiry(self):
        record = ContextRecord(
            scope=ContextScope.MEMORY,
            data={"summary": "previous task state"},
            expires_at=time.time() - 1,
        )

        assert record.expired

    def test_ucp_envelope_filters_active_context_by_scope(self):
        envelope = UCPEnvelope(
            user_id="user-1",
            agent_id="agent-1",
            contexts=[
                ContextRecord(scope=ContextScope.USER, data={"plan": "pro"}),
                ContextRecord(scope=ContextScope.TASK, data={"goal": "ship runtime"}),
                ContextRecord(scope=ContextScope.MEMORY, expires_at=time.time() - 1),
            ],
        )

        assert envelope.protocol == "ucp"
        assert len(envelope.active_contexts()) == 2
        assert envelope.active_contexts(ContextScope.TASK)[0].data == {"goal": "ship runtime"}

    def test_ucp_envelope_can_carry_action_risk_and_capability(self):
        action = ToolCallRequest(
            tool_name="github.create_pr",
            arguments={"repo": "company/backend"},
            agent_id="agent-1",
        )
        grant = CapabilityGrant(
            agent_id="agent-1",
            tool_name="github.create_pr",
            scopes=["github.pr.create"],
        )
        envelope = UCPEnvelope(
            agent_id="agent-1",
            proposed_action=action,
            risk=RiskAssessment.from_score(45, factors=["repository write"]),
            capability=grant,
        )

        assert envelope.proposed_action == action
        assert envelope.risk is not None
        assert envelope.risk.severity == Severity.MEDIUM
        assert envelope.capability is not None
        assert envelope.capability.usable
