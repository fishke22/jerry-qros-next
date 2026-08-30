# Secret Handling

Secrets never enter Git, issues, PRs, fixtures, screenshots, reports or logs.

Phase 0 defines no broker secret store because Yuanta is not authorized. Future approved secrets stay local-only and must never be printed.

If exposure occurs: treat as compromised, revoke/rotate, preserve non-secret incident evidence, remove current content, review root cause, and add a preventive control. History rewriting is not a substitute for revocation.
