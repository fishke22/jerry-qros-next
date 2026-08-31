# Contract Versioning

QROS cross-boundary truth is language-neutral JSON Schema first.

Rules:

1. Contract identity is `contract_id + contract_version`.
2. Breaking semantic or structural changes require a new major contract version.
3. Existing versions are immutable except for non-semantic documentation corrections.
4. Unknown fields are rejected by default (`additionalProperties=false`).
5. UNKNOWN is explicit data; it must never be coerced into PASS/ALLOW.
6. A validation result may classify evidence but never opens an execution or authorization gate.
7. Language-specific TypeScript/Python/C# bindings may be generated later from these contracts, but generated bindings are adapters—not the canonical contract source.
8. Broker/live-order contracts are deliberately absent until their authorized implementation phase.
