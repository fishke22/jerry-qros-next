# Phase 0 Source Evidence

Verified 2026-08-31.

## Sole authoritative Project source
- file: `deep-research-report.md`
- SHA-256: `fe954d6a3bd74d657375a67612db2c0825434559fbeaef2af1010d034914835c`
- role: SOLE AUTHORITATIVE SPECIFICATION
- repository docs machine-implement it; they do not replace it.

## Canonical repository observation
- repository: `fishke22/jerry-qros-next`
- visibility: PUBLIC
- default branch: `main`
- root before Phase 0: `README.md` only
- main commit: `d25692bbc91b8cf6aec3423525fa425ae9b34bcd`
- main tree: `687186182b40cbfd361a00c595516a5d1419e6aa`

## GitHub Actions
Official docs checked 2026-08-31: standard GitHub-hosted runners are free for public repositories; larger runners remain billed.
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/concepts/runners/larger-runners

## Secret scanning
Official docs checked 2026-08-31: public repositories have secret scanning available for free.
- https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning

## actions/checkout
- release: v6.0.2
- exact commit: `de0fac2e4500dabe0009e67214ff5f5447ce83dd`
- license: MIT
- workflow-only, not QROS runtime

## QuantConnect LEAN
- repository: `QuantConnect/Lean`
- default branch: `master`
- latest observed master commit: `b692bf4788e8b54fc23bdcb5659666bf055ce89f` (2026-08-28)
- license: Apache-2.0
- Phase 0: evidence only; integration remains deferred to Phase 3.
