# Implementation Status

## Current state

Actual product code has now started as an isolated clean-room scaffold under:

```text
product/ztx-runtime/
```

This scaffold exists in this workspace because no separate private repository path
or remote is available here yet. It should be moved to a private repository before
real product development continues beyond the prototype foundation.

## Completed in this scaffold

- package scaffold with `pyproject.toml`
- UCP envelope models
- context records with expiry handling
- adapter-neutral action request model
- deterministic decision engine v1
- explainable risk assessment
- one-time in-memory capability issuer/verifier
- in-memory approval router
- MCP-shaped adapter shim
- HTTP adapter shim
- SDK adapter shim
- local runtime orchestration
- unit tests for protocol and runtime behavior

## Not completed yet

- real private remote repository
- production persistence
- signed audit log
- real MCP process proxy
- real HTTP gateway server
- real SDK package release
- cloud policy sync
- cloud dashboard
- organization/user management
- billing or marketplace

## Next engineering step

Move or recreate `product/ztx-runtime/` in a private repository, then continue with:

1. CI workflow
2. durable audit event model
3. persistent capability store
4. first real adapter integration
5. local CLI command
