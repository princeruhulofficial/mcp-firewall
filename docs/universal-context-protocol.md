# Universal Context Protocol (UCP)

## Why UCP exists

MCP standardizes tool calling. The Zero Trust AI Execution Layer standardizes security and control. UCP is the broader context standard that lets models, agents, tools, applications, and user data exchange state in one portable structure.

UCP is not limited to MCP. MCP can be one transport and tool adapter under UCP, but UCP should also support HTTP APIs, IDE agents, CI agents, local models, cloud models, browser agents, workflow engines, and future agent runtimes.

## One-line definition

Universal Context Protocol is a shared context and action envelope that lets any AI system read context, propose actions, validate risk and permission, execute with scoped access, and preserve memory consistently.

## Problems UCP solves

Today, AI systems are fragmented:

- models use different context formats
- tools expose different schemas
- memory systems are isolated per app or vendor
- permissions are inconsistent
- audit trails are not portable
- context cannot move safely across agents or model providers

UCP gives the ecosystem one standard envelope for context, action, identity, permission, risk, and memory continuity.

## Core layers

### 1. Context Standard Layer

A portable schema for:

- user state
- task state
- memory state
- tool state
- environment state
- session state
- agent state

In code, this starts with `ContextScope`, `ContextRecord`, and `UCPEnvelope`.

### 2. Action Protocol Layer

Every action follows the same lifecycle:

1. read context
2. propose action
3. validate action
4. execute action
5. complete action

In code, this starts with `ActionPhase`.

### 3. Identity and Permission Layer

UCP carries the identities needed for enforcement:

- user identity
- agent identity
- model identity
- tool identity through the proposed action
- session identity

The Zero Trust layer uses those identities to decide who can access which tool, resource, and context.

### 4. Memory Continuity Layer

UCP makes memory portable without forcing every model or app to own the same memory store. Context records can carry compressed summaries, task history, user preferences, and tool state between sessions or providers.

### 5. Policy Execution Layer

UCP carries risk, policy decisions, approval state, and capability grants. That lets the Zero Trust AI Execution Layer enforce:

- risk scoring
- approval flows
- one-time capabilities
- audit trails
- revocation after execution

## MCP vs UCP vs Zero Trust AI Execution Layer

| System | Role |
|---|---|
| MCP | Tool calling protocol |
| UCP | Universal context and action standard |
| Zero Trust AI Execution Layer | Security and control enforcement system |

The stack should work like this:

```text
AI model / agent
      |
      v
UCP envelope: context + proposed action + identity + memory
      |
      v
Zero Trust AI Execution Layer: policy + risk + approval + capability
      |
      v
MCP / HTTP / SDK / browser / CI adapter
      |
      v
Tool / app / API / file / database / runtime
```

## UCP envelope v1

The first in-repo UCP model is intentionally small and additive:

- `protocol`: defaults to `ucp`
- `version`: schema version
- `phase`: action lifecycle phase
- `session_id`: continuity boundary
- `user_id`: user identity
- `agent_id`: agent identity
- `model_id`: model identity
- `contexts`: portable context records
- `proposed_action`: action request, currently compatible with MCP-style tool calls
- `risk`: risk assessment
- `decisions`: policy decisions
- `capability`: scoped one-time access grant
- `metadata`: extension field for integrations

## Design goals

1. **Portable:** context should move across model providers and agent frameworks.
2. **Controlled:** every proposed action should be enforceable by the Zero Trust layer.
3. **Composable:** MCP is one adapter, not the whole system.
4. **Auditable:** decisions and capabilities should be recorded with context.
5. **Privacy-aware:** sensitive context should be marked and minimized.
6. **Extensible:** vendors can add metadata without breaking the core envelope.

## Implementation roadmap

### Phase 1: Schema foundation

- Add UCP envelope and context records.
- Keep MCP request compatibility through `ToolCallRequest`.
- Add tests for context expiry and active-context filtering.

### Phase 2: UCP adapter for MCP

- Convert MCP `tools/call` requests into UCP envelopes.
- Attach agent identity, session identity, and environment context.
- Feed the envelope into risk scoring and policy evaluation.

### Phase 3: UCP policy and memory

- Add context-level sensitivity rules.
- Add memory compression and context retention settings.
- Add policy decisions that reference context scopes.

### Phase 4: Universal adapters

- Add HTTP action adapter.
- Add Python SDK adapter for non-MCP agents.
- Add CI/IDE agent adapters.

### Phase 5: Ecosystem standardization

- Publish the UCP schema.
- Create examples for common agent frameworks.
- Add conformance tests for third-party integrations.
