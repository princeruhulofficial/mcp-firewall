from __future__ import annotations

from ztx_runtime.adapters.http import envelope_from_http_request
from ztx_runtime.adapters.mcp import envelope_from_mcp_tool_call
from ztx_runtime.adapters.sdk import envelope_from_sdk_action
from ztx_runtime.approvals.router import ApprovalStatus
from ztx_runtime.capabilities.issuer import CapabilityState
from ztx_runtime.decisions.engine import DecisionOutcome
from ztx_runtime.protocol.envelope import ActionEffect, ContextRecord, ContextScope, Sensitivity
from ztx_runtime.runtime.local import LocalRuntime


def test_low_risk_action_is_allowed() -> None:
    runtime = LocalRuntime()
    envelope = envelope_from_sdk_action(
        action_type="file.read",
        name="read_notes",
        agent_id="agent-1",
        effects=[ActionEffect.READ],
    )

    result = runtime.submit(envelope)

    assert result.decision.outcome == DecisionOutcome.ALLOW
    assert result.capability is None
    assert result.approval is None


def test_medium_risk_action_gets_one_time_capability() -> None:
    runtime = LocalRuntime()
    envelope = envelope_from_http_request(
        method="POST",
        url="https://api.example.test/update",
        agent_id="agent-1",
        body={"ok": True},
    )

    result = runtime.submit(envelope)

    assert result.decision.outcome == DecisionOutcome.ISSUE_CAPABILITY
    assert result.capability is not None
    assert runtime.execute_with_capability(envelope, result.capability.id)
    assert result.capability.state == CapabilityState.CONSUMED
    assert not runtime.execute_with_capability(envelope, result.capability.id)


def test_high_risk_action_requires_approval() -> None:
    runtime = LocalRuntime()
    envelope = envelope_from_mcp_tool_call(
        tool_name="run_command",
        arguments={"command": "deploy production"},
        agent_id="agent-1",
        effects=[ActionEffect.EXECUTE, ActionEffect.NETWORK, ActionEffect.WRITE],
    )

    result = runtime.submit(envelope)

    assert result.decision.outcome == DecisionOutcome.REQUIRE_APPROVAL
    assert result.approval is not None
    approved = runtime.approvals.approve(result.approval.id, approver_id="human-1")
    assert approved.status == ApprovalStatus.APPROVED


def test_critical_risk_is_denied() -> None:
    runtime = LocalRuntime()
    envelope = envelope_from_sdk_action(
        action_type="payment.transfer",
        name="send_money",
        agent_id="agent-1",
        effects=[ActionEffect.PAYMENT, ActionEffect.ADMIN],
    )
    envelope.contexts.append(
        ContextRecord(
            scope=ContextScope.USER,
            sensitivity=Sensitivity.RESTRICTED,
            data={"account": "production"},
        )
    )

    result = runtime.submit(envelope)

    assert result.decision.outcome == DecisionOutcome.DENY
    assert result.capability is None
    assert result.approval is None
