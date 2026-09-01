# ADR-0010: Phase 3D LEAN Security Patch Candidate

Status: PROPOSED / REVIEW-GATED / RUNTIME PROMOTION DENY

Date: 2026-09-01

## Context

Phase 3B proved the QROS-owned deterministic synthetic backtest path against the exact pinned QuantConnect LEAN revision `b692bf4788e8b54fc23bdcb5659666bf055ce89f`, but runtime promotion remained blocked by known HIGH/CRITICAL dependency findings in the pinned upstream graph.

Phase 3C accepted Option A (wait for official remediation) as the default disposition. A separate, explicitly authorized Phase 3D research branch now evaluates whether a deterministic local patch can remove the known blockers without changing the LEAN gitlink, forking LEAN, introducing a paid service, enabling brokerage, or altering the QROS deterministic result contract.

## Candidate

The candidate is applied only after checkout of the unchanged exact LEAN gitlink:

1. `QuantConnect.Compression`: replace `DotNetZip 1.16.0` with `ProDotNetZip 1.20.0` while preserving the existing `Ionic.Zip` namespace used by LEAN.
2. `QuantConnect.Messaging`: remove `NetMQ 4.0.1.6` and exclude `StreamingMessageHandler.cs` from this QROS local-backtest build scope.
3. Build the standard LEAN Launcher source project with the already pinned .NET SDK.
4. Resolve the full Launcher NuGet graph and fail closed if any banned legacy blocker remains or NuGet reports any HIGH/CRITICAL vulnerability record.
5. Build the QROS synthetic algorithm and run the deterministic backtest twice.

The patch script verifies the exact LEAN revision and exact unique source anchors before modification. Any drift causes failure rather than a best-effort patch.

## Evidence required before any promotion recommendation

All of the following must be proven on the exact PR head:

- deterministic patch application PASS;
- patched standard Launcher build PASS;
- resolved graph contains `ProDotNetZip 1.20.0`;
- `DotNetZip` and `NetMQ` absent from the resolved Launcher graph;
- the known legacy `System.Drawing.Common 4.7.0` and ServiceModel/WinHttpHandler versions covered by the Phase 3 blocker are absent;
- NuGet vulnerability audit reports no HIGH/CRITICAL records;
- QROS synthetic algorithm build PASS;
- two-run deterministic backtest PASS;
- QROS normalized result remains compatible with the established Phase 3B baseline contract;
- QROS governance/contracts/supply-chain/SHA256/tests PASS;
- ProDotNetZip license and zero-cost status are verified from upstream package/source evidence;
- no Yuanta, broker credential, live trading, packaging, release, paid service, LEAN fork, or gitlink change is introduced.

UNKNOWN on any required item means DENY.

## License and cost disposition

`ProDotNetZip 1.20.0` is a NuGet package published by the upstream project. The upstream repository states that the software is released under the Microsoft Public License (Ms-PL). NuGet and the upstream repository are publicly accessible and no paid API/service/runtime is introduced by this candidate.

This is a candidate dependency used by a deterministic patch to an already-pinned open-source LEAN source tree. It is not yet recorded as an accepted QROS runtime dependency because runtime promotion remains review-gated.

## Security boundaries

This ADR does not authorize:

- changing `external/lean` gitlink;
- maintaining a QROS LEAN fork;
- silently overriding arbitrary NuGet packages;
- suppressing `NU1903` or `NU1904`;
- Yuanta integration;
- broker login or credentials;
- live trading;
- production packaging;
- GitHub Release;
- paid infrastructure or code signing.

## Decision

Phase 3D may validate this candidate as a reversible research patch. Successful CI is necessary but not sufficient for architecture acceptance.

`runtime_promotion_allowed = false`

PR #11 remains Draft until exact-head governance, security, regression, license, cost, and reproducibility evidence are reviewed. A later explicit acceptance decision is required before this ADR can move from PROPOSED to ACCEPTED and before any merge/promotion action is considered.
