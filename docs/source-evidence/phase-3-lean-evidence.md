# Phase 3 LEAN evidence — 2026-08-31

- Upstream: QuantConnect/Lean
- Latest observed master: `b692bf4788e8b54fc23bdcb5659666bf055ce89f` (2026-08-28)
- License: Apache-2.0
- Launcher target: net10.0
- Common target: net10.0
- Upstream build guidance: .NET 10; `dotnet build` on Linux.
- .NET 10 current LTS SDK selected: `10.0.400`, released 2026-08-11.
- .NET SDK license: MIT.
- actions/setup-dotnet v6.0.0 exact revision: `a98b56852c35b8e3190ac28c8c2271da59106c68`; license MIT.

Integration mode: exact public upstream gitlink + process adapter. No broker/live/Yuanta path is introduced.

## Verified build evidence

PR #5 `lean-integration` run `33402286561` / job `99521269638` completed successfully.

The job:
1. checked out QROS plus the exact LEAN submodule;
2. installed and verified .NET SDK `10.0.400`;
3. passed `scripts/validate_lean_pin.py --require-populated`;
4. built `external/lean/Launcher/QuantConnect.Lean.Launcher.csproj` in Release mode.

Duration: 1m34s.

The build emitted upstream .NET analyzer warnings in LEAN Logging classes. They are upstream warnings, not QROS-owned source changes, and did not fail the pinned source build. QROS does not patch them in the submodule.

Windows local verification had .NET SDK 10.0.301 but not exact 10.0.400, so local LEAN source build was deliberately not run with an approximate toolchain. Exact-build evidence comes from the pinned Linux CI job.
