from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ztx_runtime.protocol.envelope import (
    ActionEffect,
    ActionRequest,
    ContextRecord,
    ContextScope,
    IdentityRef,
    Sensitivity,
    UCPEnvelope,
)


def test_ucp_envelope_round_trips_json() -> None:
    envelope = UCPEnvelope(
        agent=IdentityRef(id="agent-1", kind="agent"),
        action=ActionRequest(
            type="tool.call",
            name="read_file",
            adapter="sdk",
            expected_effects=[ActionEffect.READ],
        ),
    )

    parsed = UCPEnvelope.from_json(envelope.to_json())

    assert parsed.id == envelope.id
    assert parsed.action.name == "read_file"
    assert parsed.action.expected_effects == [ActionEffect.READ]


def test_expired_context_is_filtered_out() -> None:
    now = datetime.now(UTC)
    envelope = UCPEnvelope(
        agent=IdentityRef(id="agent-1", kind="agent"),
        action=ActionRequest(type="tool.call", name="summarize", adapter="sdk"),
        contexts=[
            ContextRecord(scope=ContextScope.TASK, data={"goal": "ship"}),
            ContextRecord(
                scope=ContextScope.MEMORY,
                data={"old": True},
                expires_at=now - timedelta(seconds=1),
            ),
        ],
    )

    active = envelope.active_contexts(now=now)

    assert len(active) == 1
    assert active[0].scope == ContextScope.TASK


def test_sensitive_context_is_preserved_for_policy() -> None:
    record = ContextRecord(
        scope=ContextScope.USER,
        data={"email": "person@example.com"},
        sensitivity=Sensitivity.CONFIDENTIAL,
    )

    assert record.sensitivity == Sensitivity.CONFIDENTIAL
