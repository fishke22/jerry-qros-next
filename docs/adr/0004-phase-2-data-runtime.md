# ADR-0004 — Phase 2 Arrow-first local data runtime

- Status: Accepted
- Date: 2026-08-31
- Phase: 2

## Context

The authoritative architecture requires an immutable raw receipt followed by normalize/schema/QA, canonical Parquet, and in-process DuckDB. Pandera is Python-side QA only and must not become the cross-language contract authority.

Current official evidence supports a Windows 11 x64 Python 3.14 runtime: DuckDB 1.5.5, PyArrow 25.0.1 and Pandera 0.33.0 all support Python 3.14; Pandera 0.33.0 adds direct PyArrow Table validation.

## Decision

1. Pin CPython 3.14.7 for canonical Phase 2 CI/toolchain.
2. Use PyArrow Table as the normalized in-memory representation.
3. Use versioned JSON Schema as the language-neutral contract truth.
4. Enforce the complete canonical physical schema with PyArrow. Use Pandera's PyArrow backend only on a strict projection of demonstrably supported scalar columns, plus deterministic domain checks for decimal OHLC, volume, duplicate keys and point-in-time ordering.
5. Persist canonical historical output as Parquet.
6. Query Parquet through in-process DuckDB; do not introduce a database server.
7. Use synthetic fixtures only in this slice. No unverified external market source is promoted.
8. Raw payloads, receipts, validations and provenance are immutable-by-content and fail on conflicting rewrites.
9. UNKNOWN receipt timing blocks canonical writes.
10. PASS_REVIEW_ONLY never opens an execution or trading gate.
11. All PyPI dependencies are exact-version and wheel-hash locked for CPython 3.14 Windows x64 and Ubuntu x86-64 where platform-specific.
12. DuckDB extension auto-install/auto-load is disabled in this slice.\n13. Verified Windows smoke testing found Pandera 0.33.0/Narwhals unable to resolve `pyarrow.decimal128(18,4)` despite documentation indicating parameterized Arrow types are supported. Decimal physical typing therefore remains a PyArrow responsibility; this limitation is recorded rather than silently relaxed.

## Consequences

The first executable data path is testable on Windows and GitHub Linux CI without any broker, cloud database, daemon, paid data or product packaging.
