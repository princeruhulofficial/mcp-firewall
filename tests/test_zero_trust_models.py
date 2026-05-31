"""Tests for Zero Trust AI Execution Layer primitives."""

from __future__ import annotations

import time

from mcp_firewall.models import CapabilityGrant, CapabilityStatus, RiskAssessment, Severity


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
