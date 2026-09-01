# ADR-0011: Phase 3E Post-Merge Security and Provenance Hardening

Status: PROPOSED / REVIEW REQUIRED

Date: 2026-09-01

## Context

Post-merge review of PR #13 and PR #14 identified fail-closed gaps that were not invalidated by green CI:

- LEAN patching did not reject a dirty checkout or prove the exact post-patch diff.
- Backtest artifact identity did not bind the checkout-time patch, patched dependency graph, and built Launcher assembly.
- Structurally incomplete NuGet vulnerability JSON could be treated as evidence of no HIGH/CRITICAL advisory.
- Merge-tree evidence was recorded but not independently resolved from Git by the validator.
- The historical Phase 3C nested runtime-promotion denial was not machine-enforced.
- Historical PR #6 also identified integration path-trigger and evidence-overwrite weaknesses relevant to fail-closed operation.

These findings block Phase 4.

## Decision candidate

1. Require the exact LEAN revision and a clean worktree before patching.
2. Derive expected patched files from committed base files and verify the exact post-patch file set and contents.
3. Add `lean-backtest-result/v2` and `provenance-record/v2`; do not mutate immutable v1 schemas.
4. Bind normalized identity to patch-script SHA-256, patched-graph SHA-256, Launcher assembly SHA-256, and a canonical SHA-256 manifest over the complete Launcher output DLL closure; require Launcher, Compression, and Messaging assemblies to be present.
5. Preserve the historical Phase 3B quantitative semantic hash through an explicit v2-to-v1 semantic projection; full artifact identity remains runtime-bound.
6. Reject incomplete NuGet audit evidence unless project/framework coverage is present and matches the all-packages audit.
7. Preserve the Phase 3D accepted head under durable ref `refs/heads/evidence/phase-3d-accepted-head`, explicitly fetch that ref in governance CI, verify it still targets the recorded accepted commit, then resolve and compare the historical Git trees.
8. Enforce `next_gate.runtime_promotion_allowed=false` in the historical Phase 3C snapshot.
9. Refuse to overwrite an existing backtest evidence directory.
10. Expand integration workflow path triggers for LEAN security-policy changes.

## Boundaries

- LEAN gitlink remains `b692bf4788e8b54fc23bdcb5659666bf055ce89f`.
- Unpatched upstream runtime remains DENY.
- `PACKAGE_AUTHORIZED = false`.
- `RELEASE_AUTHORIZED = false`.
- `YUANTA_INTEGRATION_AUTHORIZED = false`.
- `LIVE_TRADING_AUTHORIZED = false`.
- Incremental dependency/license cost = 0.
- No Yuanta, broker credential, live trading, packaging, installer, release, paid service, or paid runner is introduced.

## Acceptance gate

This ADR remains proposed until the exact candidate head passes qros-gate, lean-security-research and lean-integration; two independent same-head LEAN jobs reproduce the runtime-bound normalized result and historical semantic regression; material review findings are closed; and final main integration preserves hard gates and the exact LEAN gitlink.

Passing tests alone is not production readiness.
