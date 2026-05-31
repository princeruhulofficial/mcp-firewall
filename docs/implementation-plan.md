# Implementation Plan

This plan turns the current MCP firewall into a Zero Trust AI Execution Layer with a Universal Context Protocol foundation in small, testable steps.

## Milestone 1: Establish platform primitives

Status: started.

Deliverables:

- risk assessment model with score, severity, factors, and approval requirement
- capability grant model with active, consumed, revoked, and expired lifecycle
- UCP context envelope model for non-MCP future adapters
- product architecture document
- roadmap from local MCP firewall to platform control layer

Validation:

- model unit tests
- existing test suite remains green


## Milestone 1b: Add Universal Context Protocol foundation

Status: started.

Deliverables:

- context scopes for user, task, memory, tool, environment, session, and agent state
- action phases for read, propose, validate, execute, and complete
- UCP envelope carrying context, action, risk, decisions, and capability grants
- documentation that separates MCP, UCP, and Zero Trust enforcement roles

Validation:

- expired context records are ignored
- UCP envelopes can carry proposed actions, risk, and capability grants

## Milestone 2: Add local risk scoring

Deliverables:

- convert MCP requests into UCP envelopes
- inbound `RiskScoring` pipeline stage
- static scoring rules for dangerous tools, sensitive arguments, network egress, and execution chains
- configurable score thresholds
- decision details added to audit events

Validation:

- high-risk command execution requires approval
- cloud metadata access remains denied
- read-then-send chain gets higher score

## Milestone 3: Add local capability issuer

Deliverables:

- `CapabilityIssuer` service
- issue one-time grants after allow/approval
- verify tool, agent, expiry, and constraints before execution
- consume grants after successful execution
- revoke grants when execution fails or times out

Validation:

- expired grant cannot be used
- revoked grant cannot be used
- single-use grant cannot be replayed

## Milestone 4: Replace terminal-only approval with approval router

Deliverables:

- approval request model
- local terminal approval adapter
- webhook approval adapter
- pending approval state
- approval timeout and denial defaults

Validation:

- non-interactive high-risk calls no longer auto-approve silently
- approved calls produce auditable approval evidence

## Milestone 5: Cloud connector

Deliverables:

- device identity and registration config
- policy pull endpoint client
- event upload client
- approval polling/webhook support
- offline event queue

Validation:

- runtime continues with cached policy when cloud is down
- events are retried without data loss

## Milestone 6: SaaS control plane

Deliverables:

- organizations, users, projects, agents, tools, policies
- approval dashboard
- audit event ingestion
- billing-ready usage metering
- hosted policy templates

Validation:

- one-click onboarding can configure a local MCP client
- admin can block or approve actions centrally

## Milestone 7: Marketplace and ecosystem lock-in

Deliverables:

- action/tool registry
- permission scopes
- verified tool profiles
- enterprise allowlists
- usage metering hooks

Validation:

- tool developers can publish action definitions
- enterprises can approve tools before agent usage

## Engineering rules

- Prefer additive changes until the platform boundary is stable.
- Keep local protection independent of cloud availability.
- No broad credentials should be passed to tools when a scoped capability can be used.
- High-risk non-interactive actions should fail closed once approval routing exists.
- Every platform primitive must have tests before it is enforced in the runtime.

