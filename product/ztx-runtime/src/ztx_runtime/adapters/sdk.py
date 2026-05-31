"""SDK adapter for direct Python integrations."""

from __future__ import annotations

from ztx_runtime.protocol.envelope import ActionEffect, ActionRequest, IdentityRef, UCPEnvelope


def envelope_from_sdk_action(
    *,
    action_type: str,
    name: str,
    agent_id: str,
    arguments: dict | None = None,
    effects: list[ActionEffect] | None = None,
    resource: str = "",
) -> UCPEnvelope:
    """Create an envelope from application code."""
    return UCPEnvelope(
        agent=IdentityRef(id=agent_id, kind="agent"),
        action=ActionRequest(
            type=action_type,
            name=name,
            adapter="sdk",
            resource=resource,
            arguments=arguments or {},
            expected_effects=effects or [],
        ),
    )
