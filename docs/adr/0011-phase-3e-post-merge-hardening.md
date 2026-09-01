# ADR-0011: Phase 3E Post-Merge Security and Provenance Hardening

Status: ACCEPTED / MERGED — LOCAL RESEARCH-BACKTEST HARDENING ONLY

Date: 2026-09-01

## Context

Post-merge review of Phase 3 identified fail-closed gaps that were not invalidated by green CI:

- LEAN patching did not reject a dirty checkout or prove the exact post-patch diff.
- Backtest artifact identity did not bind the checkout-time patch, patched dependency graph, and complete runtime assembly closure.
- Structurally incomplete NuGet vulnerability JSON could be treated as evidence of no HIGH/CRITICAL advisory.
- Merge-tree evidence was recorded but not independently resolved from a durable Git ref.
- The historical Phase 3C nested runtime-promotion denial was not machine-enforced.
- Historical review also identified integration path-trigger and evidence-overwrite weaknesses relevant to fail-closed operation.

## Decision

1. Require the exact LEAN revision and a clean worktree before patching.
2. Derive expected patched files from committed base files and verify the exact post-patch file set and contents.
3. Add `lean-backtest-result/v2` and `provenance-record/v2`; immutable v1 schemas remain unchanged.
4. Bind normalized identity to patch-script SHA-256, patched-graph SHA-256, Launcher assembly SHA-256, and a canonical SHA-256 manifest over the complete Launcher output DLL closure; Launcher, Compression, and Messaging assemblies are mandatory members.
5. Preserve the historical Phase 3B quantitative semantic hash through an explicit v2-to-v1 semantic projection; full artifact identity remains runtime-bound.
6. Reject incomplete NuGet audit evidence. Every framework that appears must carry list-valued `topLevelPackages` and `transitivePackages`; a clean vulnerable-output may omit frameworks entirely.
7. Preserve the Phase 3D accepted head under durable ref `refs/heads/evidence/phase-3d-accepted-head`, explicitly fetch and verify that ref in governance CI, then compare historical Git trees.
8. Enforce `next_gate.runtime_promotion_allowed=false` in the historical Phase 3C snapshot.
9. Refuse to overwrite an existing backtest evidence directory.
10. Expand integration workflow path triggers so LEAN security-policy changes cannot bypass integration validation.

## Acceptance evidence

Final accepted PR head:

`968255313ff0bff9051d50d17da335bd9da10207`

Fresh exact-head gates:

- qros-gate run `33521288679`: PASS.
- lean-security-research run `33521288691`: PASS.
- lean-integration run `33521288683`: PASS.
- same-head lean-integration jobs `99900913880` and `99901744740`: both PASS with identical runtime-bound fingerprints.

Accepted-head runtime fingerprint:

- algorithm assembly: `sha256:f63a8f9d7ef522619e6f17db06a97e2d507c2ee87fc1edd7ff297c03634b4929`
- Launcher assembly: `sha256:7338f2253306a45b0dd039c5e0d266102a9b38df79a5f411b636e75756a81c19`
- runtime assembly count: `191`
- runtime assembly manifest: `sha256:3a7b926de7e6420de31d942508662061c5e5717fa0df9de86743010374614355`
- overlay identity: `sha256:27b8d17587a2a31fd02c4ba105091e4b0c0dbdde45d1e59fdb105e4b93a65238`
- normalized result: `sha256:26f58f8d1a563d9cf6749e2d88d4449235aa2ba0c5d71c1dba8bc6168dbcc8ed`
- Phase 3B semantic regression: `sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1`
- synthetic input: `sha256:3921a0ab8ed226e6a404aca6024cf28e91100f97fb51766ecd78151c9e063e44`
- config: `sha256:4f2e7517fbf5dae1b6fe2275ce3e7fe8873d5209f7fa5b685a2f6cef9ff7e5b8`
- quantitative result: rows=5, sum=510.0000, last=104.0000, orders=0.

All material P1 review threads were addressed with exact-head evidence and resolved before merge.

## Merge closure

PR #15 was squash-merged with expected-head protection.

- integration commit: `791d99363228126e199d6cdac89857612743a2c9`
- accepted-head tree: `f49978fe60d85c642505e636e72d407ddb9745b5`
- integration tree: `f49978fe60d85c642505e636e72d407ddb9745b5`
- tree equivalence: PASS.
- post-merge main qros-gate run `33522024604`: PASS.
- post-merge LEAN gitlink: `b692bf4788e8b54fc23bdcb5659666bf055ce89f`.
- durable Phase 3E accepted-head ref: `refs/heads/evidence/phase-3e-accepted-head` → `968255313ff0bff9051d50d17da335bd9da10207`.
- governance CI explicitly fetches this ref and resolves both accepted/integration Git trees before accepting closure evidence.

## Boundaries

Phase 3E does not expand runtime authorization. It hardens the already accepted Phase 3D local Research/Backtest overlay.

- unpatched upstream LEAN runtime = DENY
- `PACKAGE_AUTHORIZED = false`
- `RELEASE_AUTHORIZED = false`
- `YUANTA_INTEGRATION_AUTHORIZED = false`
- `LIVE_TRADING_AUTHORIZED = false`
- incremental dependency/license cost = 0
- no Yuanta access, broker credential, live trading, packaging, installer, release, paid service, paid API, paid storage, GPU runner, larger runner, or code signing was introduced.

The accepted runtime scope remains:

`LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH`

This acceptance is not a production-readiness claim.
