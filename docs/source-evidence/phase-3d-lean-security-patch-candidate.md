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
