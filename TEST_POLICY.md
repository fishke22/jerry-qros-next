# Test Policy

Major phases: RESEARCH → DESIGN → IMPLEMENT → TEST → REVIEW → ACCEPT/REJECT.

Required classes grow with the system: contracts, unit, integration, regression/golden, failure/fail-closed, security/secret, data QA/provenance, Windows smoke and long-run validation.

A green suite is evidence, not a production-readiness declaration.

Phase 0 minimum: policy JSON validation, hard-gate invariants, registry required fields, secret/prohibited-file scan, pinned Action checks, approved standard runners only, and no package/release workflow.
