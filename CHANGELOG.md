# Changelog

All notable QROS Next engineering milestones are recorded here.

## Unreleased

### Phase 2
- Added the first executable Data Receipt → Arrow/Pandera QA → Parquet → DuckDB vertical slice.
- Added immutable raw receipt, validation and provenance records.
- Added point-in-time fail-closed checks and synthetic integration/failure tests.
- Pinned CPython 3.14.7 and hash-locked all Phase 2 PyPI runtime dependencies.
- Added canonical-market-bar-row/v1 language-neutral contract.

### Phase 1B
- Added fail-closed dependency registry and supply-chain policy.
- Added CycloneDX 1.7 SBOM foundation and dependency/license/source/build/provenance evidence.
- Added immutable contract digest and SHA-256 gates.

### Phase 1A
- Added versioned data/provenance/PIT/universe/validation contracts.
- Added local legacy-source promotion boundary and synthetic fixtures.

### Phase 0
- Established governance, security, cost, data-rights and packaging hard gates.
