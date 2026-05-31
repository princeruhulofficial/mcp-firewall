# Clean-Room Private Build Plan

## Decision

We will not build the private product by extending this forked MCP firewall codebase.
This repository is now treated as a **reference and research artifact only**.
The product should be implemented in a separate private repository from a blank
codebase, using our own architecture, naming, schemas, tests, and implementation.

## Why

The current repository is based on an AGPL-licensed public project. Building the
commercial product directly inside that codebase creates avoidable product,
licensing, and differentiation risk. The safer path is to use the market insight
and problem framing, then implement our own system independently.

## Product direction

The product is a **Zero Trust AI Execution Layer** with a future **Universal
Context Protocol (UCP)** standardization path.

It is not just an MCP firewall. MCP is only the first adapter.

The long-term stack is:

```text
AI model / agent
      |
      v
Universal Context Protocol envelope
      |
      v
Zero Trust execution decisioning
      |
      v
Capability-bound action execution
      |
      v
MCP / HTTP / SDK / browser / IDE / CI adapter
      |
      v
Tool / app / API / file / database / runtime
```

## Clean-room rules

1. **No source copy:** Do not copy code, tests, names, file structure, comments,
   regex lists, config examples, or implementation details from the fork.
2. **Reference only:** The fork can be used to understand the problem category,
   not as implementation material.
3. **New naming:** Use new package, CLI, config, API, and schema names.
4. **New architecture:** Build around context envelopes, action decisions,
   capability grants, approval routing, and adapters from day one.
5. **Private repository first:** The product code should start in a private repo
   with explicit license ownership before any runnable product code is written.
6. **Document provenance:** Every core module should be traceable to our product
   requirements and specs, not to the fork.
7. **Test from behavior:** Tests should describe our expected behavior, not mirror
   the fork's test cases.
8. **Separate adapters:** MCP support must be an adapter, not the core runtime.

## Next clean-room artifacts

The next planning artifacts are intentionally stored as private-product specs,
not runtime code:

- [Private Product Vision](private-product/product-vision.md)
- [UCP Envelope v1 Specification](private-product/ucp-envelope-v1-spec.md)
- [Sprint 0 Backlog](private-product/sprint-0-backlog.md)
- [Implementation Status](private-product/implementation-status.md)

## Private repository bootstrap

Create a new private repository with a neutral product name. Placeholder name:
`ztx-runtime`.

Initial structure:

```text
ztx-runtime/
├── README.md
├── LICENSE
├── pyproject.toml
├── docs/
│   ├── product-vision.md
│   ├── architecture.md
│   ├── protocol/
│   │   ├── ucp-envelope-v1.md
│   │   └── action-lifecycle.md
│   └── security/
│       ├── threat-model.md
│       └── capability-model.md
├── src/
│   └── ztx_runtime/
│       ├── __init__.py
│       ├── context/
│       ├── decisions/
│       ├── capabilities/
│       ├── approvals/
│       ├── audit/
│       ├── adapters/
│       │   ├── mcp/
│       │   ├── http/
│       │   └── sdk/
│       └── control_plane/
└── tests/
    ├── unit/
    ├── integration/
    └── conformance/
```

## Step-by-step milestones

### Milestone 0: Product and legal boundary

Deliverables:

- private repository created
- owned license selected
- clean-room rules copied into the new repository
- original fork marked as reference-only
- product name, package name, CLI name, and config name selected

Exit criteria:

- no fork-derived source code in the private repository
- repository visibility is private
- first commit contains only our docs and empty scaffolding

### Milestone 1: UCP schema foundation

Deliverables:

- UCP envelope specification
- context scopes: user, task, memory, tool, environment, session, agent
- action lifecycle: read context, propose action, validate action, execute,
  complete
- identity fields for user, agent, model, tool, organization, and workspace
- schema validation tests

Exit criteria:

- a UCP envelope can be serialized/deserialized
- expired context is ignored
- sensitive context can be tagged and minimized

### Milestone 2: Zero Trust decision engine

Deliverables:

- action request model
- decision result model
- policy input model
- risk score model
- deterministic rules engine v1
- deny / allow / require approval / issue capability decisions

Exit criteria:

- unknown high-risk actions do not execute by default
- risk score explains its factors
- every decision is auditable

### Milestone 3: Capability-based execution

Deliverables:

- one-time capability grant format
- capability issuer
- verifier
- revocation store
- expiry and replay protection

Exit criteria:

- expired capability is rejected
- revoked capability is rejected
- single-use capability cannot be replayed
- capability is bound to agent, tool, resource, and TTL

### Milestone 4: Human approval router

Deliverables:

- approval request model
- approval state machine
- local approval adapter
- webhook/Slack adapter
- timeout behavior
- auditable approver identity

Exit criteria:

- high-risk actions can pause for approval
- non-interactive high-risk actions fail closed by policy
- approval creates a scoped capability, not broad access

### Milestone 5: Adapter layer

Deliverables:

- MCP adapter as first integration
- HTTP action adapter
- Python SDK adapter
- adapter conformance tests

Exit criteria:

- MCP is not required by the core runtime
- every adapter converts incoming actions into UCP envelopes
- every adapter consumes the same decision engine

### Milestone 6: Local runtime

Deliverables:

- local daemon or CLI runtime
- local policy cache
- local audit log
- offline mode
- event queue for future cloud sync

Exit criteria:

- runtime protects actions without cloud dependency
- queued events persist across restarts
- local policy updates are validated before activation

### Milestone 7: Cloud control plane

Deliverables:

- organizations and workspaces
- users and service identities
- policy management
- approval dashboard
- audit search
- device registration
- event ingestion

Exit criteria:

- admin can define policy centrally
- local runtime syncs policy securely
- events appear in dashboard

### Milestone 8: Marketplace and ecosystem

Deliverables:

- action/tool registry
- permission scopes
- verified integrations
- conformance suite
- usage metering hooks

Exit criteria:

- third-party tools can publish action definitions
- enterprises can approve or block tools before use
- ecosystem integrations depend on our protocol and control layer

## First implementation task in the private repository

The first code task should be intentionally small:

1. create `src/ztx_runtime/protocol/envelope.py`
2. define UCP envelope dataclasses or Pydantic models
3. add serialization tests
4. add expiry handling for context records
5. run tests in CI

This creates the product foundation without relying on the fork's runtime,
pipeline, proxy, or audit implementation.

## What remains in this repository

This repository should only keep:

- upstream fork history
- reference notes
- clean-room plan
- migration decision records

The temporary scaffold in `product/ztx-runtime/` is the first clean-room code start
inside this workspace because a separate private repository is not available here.
Move it to a private repository before continuing beyond prototype work.
