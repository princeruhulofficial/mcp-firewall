"""HTTP adapter shim."""

from __future__ import annotations

from ztx_runtime.protocol.envelope import ActionEffect, ActionRequest, IdentityRef, UCPEnvelope


def envelope_from_http_request(
    *,
    method: str,
    url: str,
    agent_id: str,
    body: dict | None = None,
) -> UCPEnvelope:
    """Create an envelope from an HTTP request shape."""
    method_upper = method.upper()
    effects = [ActionEffect.NETWORK]
    if method_upper not in {"GET", "HEAD", "OPTIONS"}:
        effects.append(ActionEffect.WRITE)

    return UCPEnvelope(
        agent=IdentityRef(id=agent_id, kind="agent"),
        action=ActionRequest(
            type="http.request",
            name=method_upper,
            adapter="http",
            resource=url,
            arguments={"url": url, "method": method_upper, "body": body or {}},
            expected_effects=effects,
        ),
    )
