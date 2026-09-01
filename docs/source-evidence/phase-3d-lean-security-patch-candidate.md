# Phase 3D LEAN Security Patch Candidate Evidence

Evidence date: 2026-09-01 (Asia/Taipei)

Branch: `research/phase-3d-lean-security-patch-candidate`

PR: #11

LEAN gitlink: `b692bf4788e8b54fc23bdcb5659666bf055ce89f` (unchanged)

## Candidate scope

The Phase 3D branch does not modify the LEAN gitlink. `scripts/apply_lean_security_patch.py` validates the exact gitlink revision and exact source anchors before applying a reversible working-tree patch:

- `DotNetZip 1.16.0` -> `ProDotNetZip 1.20.0` in `Compression/QuantConnect.Compression.csproj`.
- remove `NetMQ 4.0.1.6` from `Messaging/QuantConnect.Messaging.csproj`.
- exclude `StreamingMessageHandler.cs` from the QROS local-backtest Messaging build scope.

The audit script rejects the candidate if the resolved Launcher graph still contains `DotNetZip`, `NetMQ`, `System.Drawing.Common 4.7.0`, `System.Net.Http.WinHttpHandler 4.4.0`, `System.Private.ServiceModel 4.4.0`, or `System.ServiceModel.Primitives 4.4.0`. It also rejects any NuGet vulnerability record with HIGH or CRITICAL severity and requires resolved `ProDotNetZip 1.20.0`.

## Initial exact-head CI evidence

Initial candidate head before governance evidence closure:

`e3bbf24e81a90da5a3a22a7dbe1e8d84285b473a`

GitHub Actions:

- `lean-integration` run `33480236166`: SUCCESS.
- `qros-gate` run `33480236140`: FAILURE only at `Validate SHA256SUMS` after governance, contracts, contract immutability, supply-chain evidence, LEAN security representation, and Phase 3C research-boundary validation had all passed.
- qros-gate job `99767994579` reported the exact failure: canonical Git blob SHA256 mismatch for `.github/workflows/integration-lean.yml`; tests were skipped because the fail-closed checksum step stopped the job.

Interpretation: the initial failure is provenance-manifest drift caused by the Phase 3D workflow change. It is not evidence of a compile, NuGet audit, or backtest regression. Exact-head closure still requires a fresh run after SHA/evidence updates.

## ProDotNetZip 1.20.0 upstream evidence

Official NuGet package page:

- https://www.nuget.org/packages/ProDotNetZip/1.20.0
- package: `ProDotNetZip`
- version: `1.20.0`
- published/last-updated date shown by NuGet: 2024-12-05
- target: .NET Standard 2.0
- source repository linked by NuGet: https://github.com/mihula/ProDotNetZip
- NuGet version history flags older 1.16.0/1.17.0/1.18.0 releases as having at least one high-severity vulnerability; the 1.20.0 page does not display that high-severity warning.

Upstream source repository:

- https://github.com/mihula/ProDotNetZip
- release 1.20.0 is shown as the latest repository release dated 2024-12-05.
- README states the software is open source and released under the Microsoft Public License (October 2006).
- README states the namespace remains `Ionic.Zip`, which is required for compatibility with LEAN's existing source usage.
- README documents dependencies on `System.Security.Permissions` and `System.Text.Encoding.CodePages` and states the package is AS IS; therefore QROS does not infer safety solely from the package name/version and instead audits the actual resolved Launcher graph in CI.

License disposition for candidate research use: `Ms-PL`, permissive/open-source, zero purchase cost. This evidence does not by itself authorize runtime promotion.

## Cost evidence

The candidate uses:

- the existing GitHub Actions Free infrastructure already governed by repository policy;
- NuGet public package resolution;
- local source build of the exact pinned LEAN revision;
- Python scripts stored in the repository.

No paid SaaS, paid API, paid LLM, paid market data, GPU/larger runner, cloud database, code-signing service, Yuanta service, or broker service is introduced.

`candidate_incremental_cost = 0`

## Fail-closed disposition

At this evidence checkpoint:

- `lean_gitlink_changed = false`
- `lean_fork_created = false`
- `yuanta_enabled = false`
- `live_trading_enabled = false`
- `package_authorized = false`
- `release_authorized = false`
- `runtime_promotion_allowed = false`

The candidate can only advance to an architecture review recommendation after a fresh exact-head CI run proves governance/SHA/tests plus patched build/audit/backtest evidence. Any missing or ambiguous evidence remains DENY.

## Pre-closure exact-head verification

Reviewed candidate head:

`6ba3404187ef7bc76ce81803fd1fc59984cda1d9`

GitHub Actions evidence for that exact head:

- `lean-integration` run `33486826786`, job `99788771678`: SUCCESS.
- `qros-gate` run `33486826759`, job `99788756824`: FAILURE at `Validate SHA256SUMS`; all preceding governance/contract/supply-chain/security-boundary steps passed and tests were skipped after the fail-closed checksum stop.
- Patched Launcher build completed with 0 errors.
- `validate_lean_patch_audit.py` returned `QROS patched LEAN dependency gate: PASS`, which requires resolved `ProDotNetZip 1.20.0`, rejects `DotNetZip` and `NetMQ`, rejects the established legacy blocker versions, and rejects any NuGet HIGH/CRITICAL vulnerability record.
- QROS synthetic algorithm build completed with 0 errors.
- Two-run deterministic backtest PASS.
- Phase 3D normalized result hash: `sha256:ef41d671f01d1423b4554d8aa6cdc5b1ec0a10a54ad26ec70f1267ddab35d8d0`.
- Rebuilt algorithm assembly hash: `sha256:292e722d6b8026378384bb9569e48a0c73dbcac75fc63a10da6bc326ffa4c8ea`.
- Phase 3B semantic regression hash: `sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1`: PASS.
- Quantitative fingerprint remains `qros_rows=5`, `qros_sum=510.0000`, `qros_last=104.0000`, `total_orders=0`.
- Historical Phase 3B full normalized hash remains `sha256:6da211cffdf7f667b212f9bf083d9f2d78e40b42895e6b6ed0342b76b5d6e5f1`. The Phase 3D full hash is expected to differ because the normalized provenance identity includes the rebuilt algorithm assembly hash; semantic regression is therefore evaluated with the dedicated stable projection rather than by falsifying the historical full hash.

Closure review found that the checksum manifest had not yet been synchronized for all Phase 3D source changes. The runner stopped at the first mismatch, while complete review identified drift for `.github/workflows/integration-lean.yml`, `src/qros_lean/backtest.py`, and `tests/test_lean_backtest_normalizer.py`, plus the newly introduced `scripts/validate_lean_semantic_regression.py` was not yet listed. These are provenance-manifest issues, not a demonstrated runtime regression.

Official NuGet and upstream source evidence for `ProDotNetZip 1.20.0` was re-verified on 2026-09-01 during this closure review: the NuGet package remains version 1.20.0 targeting .NET Standard 2.0 and links to the upstream `mihula/ProDotNetZip` repository; the upstream repository states Microsoft Public License (Ms-PL) and shows release 1.20.0 dated 2024-12-05. This supports zero-license-cost research use only; runtime promotion remains review-gated.

A new exact-head CI run is still required after checksum synchronization. Until that run passes both `qros-gate` and `lean-integration`, this document does not claim final Phase 3D closure.
