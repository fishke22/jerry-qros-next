# ADR-0005 — Pin LEAN as the sole canonical quant engine

- Status: Accepted
- Date: 2026-08-31
- Phase: 3A

## Decision

QROS adopts QuantConnect/Lean commit `b692bf4788e8b54fc23bdcb5659666bf055ce89f` as the exact Phase 3 quant-engine pin. Upstream remains Apache-2.0 and its Launcher/Common projects target `net10.0`.

LEAN is represented only by the `external/lean` gitlink/submodule. QROS does not fork or copy upstream source. The QROS adapter verifies revision and target framework before producing build/launch commands.

The source-build toolchain is .NET SDK `10.0.400`, pinned by `global.json` with roll-forward disabled. CI uses full-SHA-pinned `actions/setup-dotnet@a98b56852c35b8e3190ac28c8c2271da59106c68`.

Phase 3A proves exact checkout and source-build compatibility. It does not yet claim a deterministic QROS-owned LEAN backtest result. Yuanta and live brokerage remain outside this boundary.
