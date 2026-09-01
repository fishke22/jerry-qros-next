# Changelog

All notable QROS Next engineering milestones are recorded here.

## Unreleased

### Phase 3E (candidate)
- Started post-merge fail-closed hardening for exact LEAN patched-worktree verification, runtime-bound versioned backtest/provenance identity, complete NuGet audit evidence, actual Git tree verification, and historical Phase 3C denial enforcement.\n- Preserved issued v2 contracts unchanged and introduced hardened v3 runtime contracts so stricter assembly-count and patch-implementation identity rules do not rewrite historical v2 semantics.
- Kept the exact LEAN gitlink unchanged and introduced no paid dependency, packaging, release, Yuanta integration, or live trading capability.

### Phase 3D
- Merge closure: final accepted head `7b5f89a1972fd39abb78e0ad998eacf874e42739` passed independent same-head bit reproducibility and fresh PR #13 qros/security/LEAN workflows.
- Integrated Phase 3B → 3C → 3D into `main` via PR #13 squash commit `744b53c18ab433346ab01fb26d35c55e5633ba43`; post-merge Git tree is identical to accepted head tree `303e1c043c2e56093641073ab19156f46028acd1`.
- Closed historical stacked PRs #6, #7 and #11 without merge; their records remain available for traceability.
- Accepted the deterministic checkout-time LEAN security patch as the local Research/Backtest runtime overlay only.
- Kept the exact upstream LEAN gitlink unchanged and kept the unpatched upstream runtime denied.
- Frozen and validated the patched Launcher NuGet graph (55 packages / 19 projects), license evidence, and dedicated CycloneDX SBOM.
- Passed exact-head governance/SHA/tests, patched Launcher build, HIGH/CRITICAL dependency audit, deterministic backtest, and Phase 3B semantic regression.
- Kept packaging, release, Yuanta integration, and live trading hard-disabled.

### Phase 3C
- Started fail-closed LEAN dependency-remediation research on a stacked branch.
- Recorded current official upstream master/issue/PR evidence without changing the LEAN pin.
- Added an exact-pinned NuGet direct/transitive vulnerability audit workflow.
- Mapped blockers to Compression/DotNetZip and Messaging/NetMQ root-cause clusters.
- Marked Phase 3C research accepted while keeping LEAN runtime promotion hard-blocked.

### Phase 3B
- Added a QROS-owned C# synthetic algorithm and five-row local custom-data fixture.
- Added a two-run deterministic LEAN backtest normalizer with provenance and validation outputs.
- Added lean-backtest-result/v1 as a research-only, non-gate-opening contract.

### Phase 3A
- Pinned QuantConnect LEAN as the sole canonical quant engine using an external gitlink/submodule.
- Pinned .NET SDK 10.0.400 and actions/setup-dotnet v6.0.0 by immutable revision.
- Added fail-closed LEAN pin/process adapter and source-build integration gate.
- Kept Yuanta, brokerage and live trading outside the integration boundary.

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
