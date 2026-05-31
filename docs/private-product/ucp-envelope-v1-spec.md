# UCP Envelope v1 Specification

## Status

Draft for the private clean-room implementation. This is a behavioral product
specification, not copied source code.

## Goal

Define the first portable envelope that every adapter must produce before the
Zero Trust decision engine evaluates an AI action.

## Envelope fields

| Field | Required | Description |
|---|---:|---|
| `schema` | yes | Constant protocol identifier, for example `ucp.envelope`. |
| `version` | yes | Integer schema version. Starts at `1`. |
| `id` | yes | Unique envelope identifier. |
| `phase` | yes | Current lifecycle phase. |
| `organization_id` | no | Organization boundary for policy. |
| `workspace_id` | no | Workspace/project boundary for policy. |
| `user` | no | User identity block. |
| `agent` | yes | Agent identity block. |
| `model` | no | Model/provider identity block. |
| `session` | yes | Session and continuity metadata. |
| `contexts` | yes | List of context records. May be empty. |
| `action` | yes | Proposed action block. |
| `risk` | no | Risk assessment block added by the decision engine. |
| `decision` | no | Decision block added by the decision engine. |
| `capability` | no | Capability grant added after allow or approval. |
| `audit` | no | Audit metadata added by runtime. |
| `extensions` | no | Namespaced adapter-specific metadata. |

## Lifecycle phases

1. `read_context`
2. `propose_action`
3. `validate_action`
4. `await_approval`
5. `issue_capability`
6. `execute_action`
7. `complete_action`
8. `revoke_capability`
9. `record_audit`

## Context record

A context record represents portable state. Minimum fields:

| Field | Required | Description |
|---|---:|---|
| `id` | yes | Unique context record identifier. |
| `scope` | yes | One of `user`, `task`, `memory`, `tool`, `environment`, `session`, `agent`. |
| `subject` | no | Entity the context belongs to. |
| `data` | yes | Structured JSON-compatible data. |
| `sensitivity` | yes | `public`, `internal`, `confidential`, `restricted`. |
| `created_at` | yes | Creation timestamp. |
| `expires_at` | no | Expiry timestamp. Expired records must not be used for decisions. |
| `source` | no | Adapter or service that produced the record. |

## Action block

The action block describes what the AI wants to do, independent of adapter.

| Field | Required | Description |
|---|---:|---|
| `type` | yes | Action category, such as `tool.call`, `http.request`, `file.read`, `command.run`. |
| `name` | yes | Adapter-level action name. |
| `resource` | no | Target resource identifier. |
| `arguments` | yes | JSON-compatible argument payload. |
| `expected_effect` | no | `read`, `write`, `execute`, `network`, `admin`, `payment`, or combined effects. |
| `adapter` | yes | Adapter that produced the action, such as `mcp`, `http`, `sdk`, `browser`. |

## Decision block

Decision outcomes:

- `allow`
- `deny`
- `require_approval`
- `issue_capability`
- `sandbox`
- `monitor_only`

Every decision must include:

- reason code
- human-readable reason
- policy references
- risk score reference
- timestamp

## Capability block

A capability grant must be:

- scoped to organization/workspace when available
- bound to agent identity
- bound to action type and name
- bound to resource constraints
- short-lived
- single-use by default
- revocable
- auditable

## Adapter requirements

Every adapter must:

1. parse its native request format;
2. build a UCP envelope;
3. call the decision engine;
4. execute only if allowed or capability-backed;
5. consume or revoke the capability;
6. emit an audit event.

## Non-goals for v1

- No cloud dependency in the envelope.
- No marketplace metadata in the core schema.
- No provider-specific model format in required fields.
- No direct dependency on MCP structures.
