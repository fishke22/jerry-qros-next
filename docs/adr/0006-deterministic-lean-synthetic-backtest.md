# ADR-0006 — Deterministic QROS-owned synthetic LEAN backtest

- Status: ACCEPTED AS RESEARCH/BACKTEST CONTRACT; RUNTIME AUTHORITY CONTINUES IN ADR-0010
- Date: 2026-08-31
- Phase: 3B
- Closure: 2026-09-01

## Decision

Phase 3B proves the QROS → LEAN process boundary with QROS-owned inputs instead of LEAN regression fixtures.

The test algorithm is QROS-owned C# source compiled against the exact pinned LEAN source tree. It reads exactly five local synthetic observations through a custom BaseData source using SubscriptionTransportMedium.LocalFile. Live mode is rejected.

The algorithm submits no orders. It validates the observations inside LEAN and writes deterministic summary statistics: row count 5, close sum 510.0000, last close 104.0000 and total orders 0.

The integration runner launches the pinned LEAN Launcher twice with the same assembly, local fixture and backtesting config. QROS normalizes only stable result fields and requires the two normalized result objects to be identical.

Raw LEAN result files are represented by SHA-256 in provenance. Non-deterministic raw metadata is not promoted into normalized quant truth.

## Gate

ACCEPT only after exact .NET 10.0.400 CI executes both backtests successfully and the normalized result is deterministic. The result remains research-only and cannot open any execution or live-trading gate.

## Closure note

The functional and determinism criteria were subsequently satisfied and independently revalidated during Phase 3D. ADR-0010 is the current authority for whether a LEAN runtime may be promoted. It permits only the deterministic Phase 3D patched local Research/Backtest runtime and keeps the unpatched upstream runtime, packaging, release, Yuanta integration, and live trading denied.
