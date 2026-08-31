# ADR-0006 — Deterministic QROS-owned synthetic LEAN backtest

- Status: Proposed
- Date: 2026-08-31
- Phase: 3B

## Decision

Phase 3B proves the QROS → LEAN process boundary with QROS-owned inputs instead of LEAN regression fixtures.

The test algorithm is QROS-owned C# source compiled against the exact pinned LEAN source tree. It reads exactly five local synthetic observations through a custom BaseData source using SubscriptionTransportMedium.LocalFile. Live mode is rejected.

The algorithm submits no orders. It validates the observations inside LEAN and writes deterministic summary statistics: row count 5, close sum 510.0000, last close 104.0000 and total orders 0.

The integration runner launches the pinned LEAN Launcher twice with the same assembly, local fixture and backtesting config. QROS normalizes only stable result fields and requires the two normalized result objects to be identical.

Raw LEAN result files are represented by SHA-256 in provenance. Non-deterministic raw metadata is not promoted into normalized quant truth.

## Gate

ACCEPT only after exact .NET 10.0.400 CI executes both backtests successfully and the normalized result is deterministic. The result remains research-only and cannot open any execution or live-trading gate.
