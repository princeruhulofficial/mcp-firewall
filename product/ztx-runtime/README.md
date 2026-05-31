# ZTX Runtime

Clean-room starter implementation for a Zero Trust AI Execution Layer.

This is the first private-product scaffold. It does not reuse the forked MCP
firewall runtime. MCP is treated as one adapter; the core runtime operates on
UCP envelopes.

## What works now

- UCP envelope models
- context expiry and sensitivity metadata
- action request model
- deterministic decision engine v1
- in-memory one-time capability issuer/verifier
- in-memory approval router
- MCP, HTTP, and SDK adapter shims
- local runtime orchestration
- unit tests

## Run tests

```bash
python -m pytest
```
