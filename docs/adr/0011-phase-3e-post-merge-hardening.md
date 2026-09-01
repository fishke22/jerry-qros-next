# ADR-0011: Phase 3E Post-Merge Security and Provenance Hardening

Status: ACCEPTED

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

## Decision

1. Require the exact LEAN revision and a clean worktree before patching.
2. Derive expected patched files from committed base files and verify the exact post-patch file set and contents.
3. Preserve immutable `lean-backtest-result/v2` and `provenance-record/v2` exactly as issued; publish hardened `lean-backtest-result/v3` and `provenance-record/v3` for the stricter runtime identity.
4. Bind normalized identity to the actual patch wrapper SHA-256, a separately named patch implementation SHA-256, patched-graph SHA-256, Launcher assembly SHA-256, and a canonical SHA-256 manifest over the complete Launcher output DLL closure; require Launcher, Compression, and Messaging assemblies to be present.
5. Preserve the historical Phase 3B quantitative semantic hash through an explicit current-to-v1 semantic projection; full artifact identity remains runtime-bound.
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

## Acceptance evidence

Accepted candidate head: `1598c320eeacf452519b8fd7ae8195d928ec74e5`.

- PR #18: squash-merged to `main` as `6b08e0cd0bb3536e2f01d88e2bf540d20db54a23`.
- Accepted-head tree and merge-commit tree: `dee4a39e3bc4caf937755768d2ed7278191415ff` — exact tree equivalence PASS.
- `qros-gate` run `33529365184`, job `99928262098`: SUCCESS.
- `lean-security-research` run `33529365278`, job `99929955725`: SUCCESS.
- `lean-integration` run `33529364975`: attempt 1 job `99928609619` SUCCESS and independent same-head attempt 2 job `99929572680` SUCCESS.
- Both LEAN jobs reproduced normalized hash `sha256:43153f0cc229a6c55005581678cbcf02002e9377c4939115e92d4fd5c48e2881`, overlay identity `sha256:cd78ab7cea3f10608989c44be1f9bd4c162c04895a21cca77de55ccee5901525`, runtime assembly count `191`, runtime assembly manifest `sha256:3a7b926de7e6420de31d942508662061c5e5717fa0df9de86743010374614355`, and historical semantic regression `sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1`.
- Exact-head Codex review at `1598c320ee` produced no P1/P2 after remediation. The only P3 Markdown formatting item was tracked as Issue #19 and is corrected by the governance closure slice.
- Post-merge `main` qros-gate run `33530330017`, job `99931568789`: SUCCESS.
- Exact LEAN gitlink remains `b692bf4788e8b54fc23bdcb5659666bf055ce89f`.
- Packaging, release, Yuanta integration, and live trading remain DENY.

Detailed closure evidence is recorded in `docs/source-evidence/phase-3e-merge-closure.md`.

Passing these gates accepts only the hardened local Research/Backtest runtime scope. It is not a production-readiness claim.
