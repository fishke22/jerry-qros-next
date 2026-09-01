# ADR-0010: Phase 3D LEAN Security Patch Runtime Overlay

Status: ACCEPTED / LOCAL RESEARCH-BACKTEST RUNTIME ONLY

Date: 2026-09-01

## Context

The exact pinned QuantConnect LEAN revision `b692bf4788e8b54fc23bdcb5659666bf055ce89f` remains the sole canonical quant-engine source revision. Its unmodified upstream dependency graph contains the Phase 3B HIGH/CRITICAL blockers recorded in `config/lean-security-review.json`, so the unpatched runtime remains denied.

Phase 3D evaluated a deterministic checkout-time QROS patch without changing the LEAN gitlink, maintaining a LEAN fork, suppressing NuGet advisories, introducing a paid service, enabling brokerage, or changing the QROS quantitative result contract.

## Accepted runtime overlay

The accepted overlay is applied only after validating the exact unchanged LEAN gitlink and exact source anchors:

1. `QuantConnect.Compression`: replace `DotNetZip 1.16.0` with `ProDotNetZip 1.20.0` while preserving the `Ionic.Zip` API surface used by the pinned LEAN source.
2. `QuantConnect.Messaging`: remove `NetMQ 4.0.1.6` and exclude `StreamingMessageHandler.cs` from the QROS local Research/Backtest Launcher scope.
3. Restore the standard patched Launcher once, freeze and verify the resolved NuGet graph, and use `--no-restore` for subsequent package-list/build steps.
4. Fail closed if the frozen graph, license evidence, CycloneDX SBOM, banned-package set, HIGH/CRITICAL audit, source anchors, or deterministic regression evidence drifts.

`runtime_promotion_scope = LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH`

`baseline_unpatched_upstream_runtime_allowed = false`

## Acceptance evidence

Exact acceptance prerequisite head: `4050b640f54fab9b0fda28c7d73145a0e44a4294`.

- `qros-gate` run `33503647209`, job `99842494385`: SUCCESS, including canonical SHA256SUMS and full tests.
- `lean-integration` run `33503647152`, job `99842494995`: SUCCESS.
- Patched Launcher build: 0 errors.
- Patched dependency audit: PASS.
- Frozen NuGet graph: 55 packages, 19 project nodes, graph SHA-256 `165ba17fec034b417f4ae91b86544cbe9b2002f1c561f4908b0d43a76875f235`.
- License gate: PASS, 44 NuGet SPDX metadata dispositions plus 11 manual reviews; no UNKNOWN remains.
- Patched Launcher CycloneDX SBOM gate: PASS, 55 packages.
- QROS synthetic algorithm build: 0 errors.
- Two-run deterministic backtest: PASS.
- Phase 3B semantic regression hash: `sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1`.
- Quantitative fingerprint: `qros_rows=5`, `qros_sum=510.0000`, `qros_last=104.0000`, `total_orders=0`.

An independent same-revision rerun on an earlier Phase 3D head reproduced the algorithm assembly bit-for-bit. Cross-commit assembly hashes remain provenance-sensitive by design; cross-revision quantitative stability is enforced by the semantic regression projection.

## License and cost disposition

The canonical transitive license inventory is stored in `supply-chain/lean/launcher-patched-nuget-license-metadata.json` and `config/lean-nuget-license-dispositions.json`.

`ProDotNetZip 1.20.0` is treated as a multi-origin package whose applicable upstream portions include MS-PL, BSD-3-Clause, Zlib, Apache-2.0, MIT, and an LZMA SDK public-domain notice. It is not represented as a single-license package.

The runtime overlay introduces no paid SaaS, API, LLM, market data, cloud database, GPU/larger runner, storage, code-signing service, brokerage service, or other paid dependency.

`candidate_incremental_cost = 0`

## Distribution boundary

Acceptance of this local runtime does not authorize distribution or production release. Some transitive packages, including Accord 3.6.0 under LGPL-2.1-or-later, carry distribution obligations that require a separate review if packaging is ever authorized.

The following gates remain closed:

- `PACKAGE_AUTHORIZED = false`
- `RELEASE_AUTHORIZED = false`
- `YUANTA_INTEGRATION_AUTHORIZED = false`
- `LIVE_TRADING_AUTHORIZED = false`

No installer, MSI, NSIS, MSIX, production EXE package, GitHub Release, auto-update channel, code signing, broker credential, broker login, or real order is authorized by this ADR.

## Decision

Accept the deterministic Phase 3D checkout-time security patch as the QROS LEAN runtime overlay for local Research/Backtest only.

`runtime_promotion_allowed = true`

This boolean is valid only together with the restricted runtime scope above. The unpatched upstream LEAN runtime remains denied. Any drift in the exact LEAN gitlink, patch anchors, resolved graph, license disposition, SBOM, vulnerability audit, quantitative regression, or hard-gate state returns the runtime to DENY.

This acceptance is not a production-readiness claim.
