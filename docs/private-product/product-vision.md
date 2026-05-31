# Private Product Vision

## Working product name

Use a temporary internal name until branding is finalized: **ZTX Runtime**.

The name is only a placeholder. The private repository should choose its own
package, CLI, service, and config names before implementation starts.

## Product thesis

AI systems should not call tools, APIs, files, databases, browsers, payment
systems, or production infrastructure directly. Every AI action should pass
through a control layer that can understand context, evaluate intent, score risk,
request approval, grant temporary access, execute through an adapter, and revoke
access after completion.

The product is therefore a **Zero Trust AI Execution Layer** with a future
**Universal Context Protocol** path.

## What we are building

A private, clean-room runtime and control plane for AI action execution:

1. **Universal context envelope**: one standard structure for user, task, memory,
   tool, environment, session, and agent state.
2. **Action decision engine**: deterministic policy and risk evaluation before
   execution.
3. **Capability system**: short-lived, one-time grants for the exact action that
   was approved.
4. **Approval router**: human escalation for high-risk actions.
5. **Adapter layer**: MCP, HTTP, SDK, browser, IDE, and CI adapters convert
   external actions into the same internal envelope.
6. **Local runtime**: offline-capable enforcement on developer or server systems.
7. **Cloud control plane**: organization policy, approvals, audit search, device
   registration, and analytics.
8. **Action marketplace**: verified tools, permission scopes, conformance tests,
   and usage metering.

## What we are not building first

- Not another MCP-only firewall.
- Not a direct fork of the reference repository.
- Not a prompt-injection regex product.
- Not a SaaS dashboard before the local runtime primitives are correct.
- Not a marketplace before adapters and conformance are stable.

## Primary users

### Developer

Wants to safely use AI agents with local tools, files, terminals, browsers, and
MCP servers without exposing credentials or production resources.

### Team admin

Wants shared policies, approval flows, and audit visibility across many AI tools
and developers.

### Enterprise security team

Wants default-deny control, identity-aware policies, just-in-time access,
revocation, SIEM-ready audit, and clear evidence for compliance.

### Tool developer

Wants a standard way to publish tool capabilities, permission scopes, risk
metadata, and conformance evidence.

## Product principles

1. **Context first:** decisions must see task, user, memory, tool, environment,
   and session state.
2. **MCP is an adapter:** the core must support non-MCP actions from day one.
3. **Least privilege:** tools receive scoped capabilities, not broad credentials.
4. **Fail closed for high risk:** when approval or policy cannot be evaluated,
   high-risk actions do not execute.
5. **Local enforcement:** the runtime must protect users without cloud access.
6. **Cloud coordination:** the cloud control plane coordinates policy, approvals,
   and audit, but does not become a single point of execution failure.
7. **Clean-room provenance:** implementation comes from these private product
   specs, not from the reference fork.

## North-star workflow

```text
Agent proposes action
  -> Runtime wraps it in a UCP envelope
  -> Decision engine evaluates policy and risk
  -> Low risk: issue scoped capability
  -> High risk: request human approval
  -> Approved action executes through adapter
  -> Capability is consumed or revoked
  -> Audit event is recorded locally and synced to cloud
```

## MVP boundary

The first MVP should prove only four things:

1. a UCP envelope can represent actions from more than one adapter shape;
2. the decision engine can produce explainable allow/deny/approval outcomes;
3. capability grants can prevent replay and over-broad execution;
4. a local runtime can enforce decisions without a cloud dependency.
