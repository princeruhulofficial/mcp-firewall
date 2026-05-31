"""MCP adapter shim.

This file intentionally does not import an MCP SDK. It converts MCP-shaped data
into the internal UCP envelope so the core runtime stays adapter-neutral.
"""

from __future__ import annotations

from ztx_runtime.protocol.envelope import ActionEffect, ActionRequest, IdentityRef, UCPEnvelope


def envelope_from_mcp_tool_call(
    *,
    tool_name: str,
    arguments: dict,
    agent_id: str,
    effects: list[ActionEffect] | None = None,
) -> UCPEnvelope:
    """Create an envelope from MCP tools/call-like data."""
    return UCPEnvelope(
        agent=IdentityRef(id=agent_id, kind="agent"),
        action=ActionRequest(
            type="tool.call",
            name=tool_name,
            adapter="mcp",
            arguments=arguments,
            expected_effects=effects or [],
        ),
    )
