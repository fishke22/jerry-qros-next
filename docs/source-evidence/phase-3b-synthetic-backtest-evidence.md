# Phase 3B synthetic backtest evidence

## Research basis

- The pinned LEAN custom BaseData interface supports SubscriptionTransportMedium.LocalFile.
- The pinned Launcher command-line parser supports explicit config file, algorithm type/location, data folder, results destination and close-automatically.
- BacktestingResultHandler stores final backtest results under the configured results destination.
- BaseResultsHandler serializes result properties with CamelCaseNamingStrategy, so the pinned result JSON field is `statistics`.
- QROS invokes the pinned Apache-2.0 LEAN source build directly; no paid LEAN CLI is introduced.
- The synthetic fixture is QROS-owned and contains no market data or redistribution-rights dependency.
- Messaging is the LEAN local/desktop implementation. Api.Initialize constructs a client; this synthetic backtest path does not invoke authenticated API operations.

## Functional acceptance evidence

Run `33405771315` / job `99532872381` succeeded on exact .NET SDK 10.0.400 and Python 3.14.7.

Verified sequence:

1. exact LEAN gitlink checkout and pin validation — PASS;
2. pinned LEAN Launcher Release source build — PASS;
3. QROS-owned C# synthetic algorithm build — PASS;
4. deterministic QROS → LEAN backtest executed twice — PASS;
5. normalized results matched — PASS;
6. Total Orders = 0;
7. normalized result hash = `sha256:6da211cffdf7f667b212f9bf083d9f2d78e40b42895e6b6ed0342b76b5d6e5f1`.

## Security review

The same successful build emitted blocking NuGet vulnerability warnings for the pinned LEAN dependency graph:

- DotNetZip 1.16.0 — HIGH — GHSA-xhg6-9j5j-w4vf.
- System.Drawing.Common 4.7.0 — CRITICAL — GHSA-rxg9-xrhp-64gj.
- System.Net.Http.WinHttpHandler 4.4.0 — HIGH — GHSA-6xh7-4v2w-36q6.
- System.Private.ServiceModel 4.4.0 — HIGH — GHSA-jc8g-xhw5-6x46.
- System.ServiceModel.Primitives 4.4.0 — HIGH — GHSA-jc8g-xhw5-6x46.

DotNetZip is a direct dependency of `external/lean/Compression/QuantConnect.Compression.csproj`; the reviewed advisory lists no patched DotNetZip version. QuantConnect/Lean issue #8795 remains open requesting replacement of the unmaintained dependency.

The existing QROS CycloneDX file records LEAN as one top-level component but does not enumerate the full NuGet transitive graph. Therefore the LEAN transitive SBOM is also incomplete for runtime promotion.

## Phase 3B disposition

**FUNCTIONAL PASS / SECURITY BLOCKED.**

The backtest result remains research-only and review-only. Phase 3B must not merge or promote LEAN runtime use until the blocker in `config/lean-security-review.json` is resolved through a reviewed architecture amendment and regression evidence.
