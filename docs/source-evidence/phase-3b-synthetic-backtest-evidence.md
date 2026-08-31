# Phase 3B synthetic backtest evidence

## Research basis

- The pinned LEAN custom BaseData interface supports SubscriptionTransportMedium.LocalFile.
- The pinned Launcher command-line parser supports explicit config file, algorithm type/location, data folder, results destination and close-automatically.
- BacktestingResultHandler stores final backtest results under the configured results destination.
- QROS invokes the pinned Apache-2.0 LEAN source build directly; no paid LEAN CLI is introduced.
- The synthetic fixture is QROS-owned and contains no market data or redistribution-rights dependency.
- Messaging is the LEAN local/desktop implementation and only writes result/debug packets to local logging.
- Api.Initialize constructs a client but this backtest path does not invoke authenticated API operations.

## Acceptance

PENDING CI execution.
