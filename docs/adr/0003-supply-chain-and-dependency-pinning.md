# ADR-0003 — Supply-chain evidence and dependency pinning baseline

- Status: Accepted
- Date: 2026-08-31
- Phase: 1B

## Context

QROS Next requires zero-cost, license-aware, provenance-first dependency governance. The architecture authority requires SBOM, SHA256SUMS, dependency-license manifest, source revision, build environment and provenance manifest at candidate milestones. It also requires exact dependency pins and treats UNKNOWN as DENY.

Phase 1B has no product runtime. Prematurely choosing versions for Phase 2/3/4/6 components would create false stability and stale pins before their implementation review.

## Decision

1. Only dependencies actually used by the repository may have status `ADOPTED`.
2. `ADOPTED` requires exact revision, verified license, proven zero-cost class and the required lock discipline.
3. Future runtime candidates remain `PLANNED_DENY_USE_UNTIL_PINNED` with `UNSPECIFIED` versions until their implementation phase.
4. CycloneDX 1.7 JSON is the machine SBOM format.
5. Phase 1B SBOM truthfully contains zero runtime components.
6. Existing v1 contract schema files are immutable by recorded Git blob digest. Semantic/breaking changes require a new version file.
7. GitHub Actions remain full-SHA pinned and least-privilege.
8. The repository's own source license is not inferred from public visibility; until a LICENSE decision is made, status is `NO_LICENSE_FILE`.

## Consequences

- No dependency is approved merely because it appears in the architecture.
- Phase 2+ must perform official version/license/cost research immediately before introduction.
- Supply-chain evidence is available before product build tooling exists.
- Contract drift fails closed.
