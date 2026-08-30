# Dependency Policy

1. Core dependency license must be verified before merge. UNKNOWN LICENSE = DENY.
2. Exact versions/revisions are pinned before introduction; `UNSPECIFIED` is not approved.
3. Prefer permissive OSS → free official API/public data → public standard GitHub CI → local execution.
4. Paid, metered-overage, GPU/larger-runner-only, AGPL/proprietary/restrictive or unclear dependencies are denied pending review.
5. Development tools do not become QROS runtime dependencies by convenience.
6. Record purpose, revision, license/terms, cost, data rights when relevant, fallback and exit strategy.
7. Lockfiles are mandatory once an ecosystem is introduced.
8. Candidate builds require SBOM, SHA-256, source revision, build environment and dependency-license manifest.
