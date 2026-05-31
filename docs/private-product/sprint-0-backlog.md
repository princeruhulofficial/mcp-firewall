# Sprint 0 Backlog: Private Clean-Room Bootstrap

## Sprint goal

Create the private repository foundation without importing source code from the
reference fork. Sprint 0 ends when the private repository has product specs,
empty package scaffolding, CI, and the first UCP envelope tests.

## Required decisions before coding

- final internal repository name
- package name
- CLI name
- license and copyright owner
- primary language and runtime
- Pydantic/dataclass/schema library choice
- CI provider
- secret scanning policy

## Tasks

### ZTX-0: Create private repository

Acceptance criteria:

- repository visibility is private
- first commit contains no copied fork source
- clean-room rules are included
- branch protection is enabled before product code lands

### ZTX-1: Add product docs

Acceptance criteria:

- `docs/product-vision.md` exists
- `docs/architecture.md` exists
- `docs/protocol/ucp-envelope-v1.md` exists
- `docs/security/capability-model.md` exists
- docs cite product requirements, not fork internals

### ZTX-2: Add empty package scaffold

Acceptance criteria:

- package imports successfully
- no runtime behavior is implemented yet
- public API surface is explicitly marked unstable

### ZTX-3: Implement UCP envelope v1 models

Acceptance criteria:

- envelope serializes to JSON
- envelope deserializes from JSON
- context records can expire
- action block supports at least two adapter types in tests
- no MCP-specific dependency is required by the core model

### ZTX-4: Add test and quality gates

Acceptance criteria:

- unit tests run in CI
- formatting/linting is configured
- type checking is configured if the language supports it
- dependency audit or lockfile review is configured

### ZTX-5: Add provenance checklist

Acceptance criteria:

- each module has an owner and requirement reference
- PR template asks whether fork code was copied
- contribution rules prohibit copying source from reference projects

## Out of scope

- MCP adapter implementation
- risk scoring implementation
- capability issuer implementation
- cloud dashboard
- marketplace

## Sprint 0 exit checklist

- [ ] private repo exists
- [ ] clean-room rules committed
- [ ] docs committed
- [ ] package scaffold committed
- [ ] UCP envelope tests pass
- [ ] no fork-derived source copied
- [ ] next sprint backlog approved
