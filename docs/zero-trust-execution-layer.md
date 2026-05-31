# Zero Trust AI Execution Layer

## Positioning

mcp-firewall should evolve from a single MCP security tool into a **Zero Trust AI Execution Layer**: a default control plane and runtime guard between AI agents, MCP servers, tools, APIs, files, databases, and production systems.

The core thesis is simple:

> Every AI action is untrusted until identity, policy, risk, approval, and capability checks prove it is safe enough to execute.

This shifts the product from "scanner/firewall" to "execution control".

## Market stage thesis

### Stage A: Tools

The current repository is in this stage. It provides an MCP proxy, policy checks, audit logging, response scanning, and SDK-style integration points.

### Stage B: Platform

The next goal is to become the default layer that AI tools integrate with for action authorization. At this stage the product controls identity, policy, risk scoring, just-in-time permissions, approvals, and audit.

### Stage C: Infrastructure standard

The long-term goal is to become a standard execution layer for agentic systems, similar to how identity providers, API gateways, and zero-trust network layers became default infrastructure.

## Product principles

1. **Deny by default for unknown risk.** Unknown agent, tool, destination, or data flow should be treated as suspicious.
2. **Authorize actions, not just users.** Every tool call should be evaluated with its arguments and session context.
3. **Issue least-privilege capabilities.** Tools should receive short-lived, scoped, one-time grants instead of broad credentials.
4. **Escalate high risk to humans.** High-risk actions should route to approval workflows with evidence and expiry.
5. **Revoke after execution.** Access should be consumed or revoked when the requested action finishes or expires.
6. **Record tamper-evident audit.** Every decision and execution outcome should be traceable.
7. **Run locally when needed, sync centrally when possible.** The data plane should keep protecting users even when the cloud control plane is temporarily unavailable.

## Target architecture

```text
AI Agent / Model
      |
      v
Zero Trust AI Execution Layer
      |
      +-- Identity Resolver
      +-- Policy Engine
      +-- Risk Scoring Engine
      +-- Capability Issuer
      +-- Human Approval Router
      +-- Audit and Telemetry
      |
      v
MCP Server / Tool / API / Database / Runtime
```

## Runtime decision flow

1. Agent requests a tool action.
2. Runtime builds an action context: agent, user, tool, arguments, resource, session, history, and environment.
3. Policy engine checks allow/deny/prompt rules.
4. Risk engine scores the action using static rules and behavioral history.
5. Low-risk action may be allowed directly or via a one-time capability.
6. Medium-risk action may require scoped capability and extra monitoring.
7. High-risk action is escalated to human approval.
8. Approved action receives a short-lived capability.
9. Tool execution happens using only that capability.
10. Capability is consumed or revoked.
11. Decision and outcome are logged to the audit trail.

## One-time capability lifecycle

```text
requested -> evaluated -> issued -> used -> consumed
                      \-> denied
                      \-> escalated -> approved -> issued
                                  \-> rejected
issued -> expired
issued -> revoked
```

A capability should be:

- **single-use** by default
- **short-lived** by default
- bound to **agent identity**
- bound to **tool name**
- bound to **resource constraints**
- invalid after completion, timeout, or explicit revocation

## Risk scoring inputs

Initial risk factors:

- tool category: read, write, execute, network, database, payment, credential, admin
- destination: public internet, private network, cloud metadata, unknown domain
- data sensitivity: secrets, PII, financial, health, production config
- action chain: read -> send, read -> execute, list -> exfiltrate
- agent identity and trust level
- user/org policy
- environment: local dev, CI, staging, production
- historical anomaly: new tool, new destination, unusual frequency

Default score bands:

| Score | Severity | Default action |
|---:|---|---|
| 0-9 | info | allow/monitor |
| 10-39 | low | allow with audit |
| 40-69 | medium | issue scoped capability |
| 70-89 | high | human approval |
| 90-100 | critical | deny or emergency approval |

## Product roadmap

### Phase 1: Runtime kernel

- Keep the existing MCP proxy and pipeline working.
- Add risk assessment models.
- Add one-time capability grant models.
- Add decision metadata needed for cloud approvals.
- Expand tests so the primitives are stable.

### Phase 2: Local enforcement

- Add a risk-scoring stage to the inbound pipeline.
- Add a local capability issuer and verifier.
- Bind capability grants to exact tool/action/resource constraints.
- Consume or revoke capability after execution.
- Fail closed for high-risk actions when approval is unavailable.

### Phase 3: Cloud control plane

- Device registration and API-key based local agent identity.
- Policy sync from cloud to local runtime.
- Event upload with offline queue.
- Human approval workflow via web dashboard, Slack, or webhook.
- Central audit search and SIEM export.

### Phase 4: Universal adapters

- MCP remains the first integration.
- Add SDK adapters for common agent frameworks.
- Add HTTP/API gateway mode for non-MCP actions.
- Add CI/CD and IDE agent integrations.

### Phase 5: Action marketplace

- Tool registry with permissions and risk metadata.
- Verified tool profiles.
- Enterprise allowlists.
- Usage metering and payment hooks.
- Developer distribution layer.

## Migration from current repository

The current codebase should become the first local data plane. The immediate changes should be additive and backwards-compatible:

- keep current CLI and SDK behavior stable
- add platform primitives without forcing cloud dependency
- keep tests passing after every step
- document the higher-level platform direction
- later split cloud control plane into a separate service boundary

