# Implementation Roadmap

Execution model: RESEARCH → DESIGN → IMPLEMENT → TEST → REVIEW → ACCEPT/REJECT.

1. Phase 0 — Governance implementation
2. Phase 1 — Repository foundation + versioned contracts
3. Phase 2 — Data receipt / QA / Parquet / DuckDB vertical slice
4. Phase 3 — Pinned LEAN integration — **ACCEPTED / MERGED** for local Research/Backtest only through the deterministic Phase 3D runtime overlay
5. Phase 3E — Post-merge security/provenance hardening — **ACCEPTED / MERGED**
6. Phase 4 — QUT Tauri/React zh-TW shell — **RESEARCH COMPLETE / CURRENT GATE: DESIGN REVIEW**
7. Phase 5 — Research / Backtest / Data QA workspace
8. Phase 6 — Internal AI API + one zero-cost local provider
9. Phase 7 — Mock/Paper Broker + deterministic Safety
10. Phase 8 — Integrated end-to-end verification
11. Phase 9 — Windows CI/local Windows/Norton-Defender/long-run validation
12. PRE-PACKAGING READINESS — HARD STOP

Phase 3 closure: PR #13 integrated the accepted Phase 3B → 3C → 3D stack into `main`. The exact upstream LEAN gitlink remains pinned at `b692bf4788e8b54fc23bdcb5659666bf055ce89f`. The unpatched upstream runtime remains DENY; only `LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH` is allowed.

Phase 3E closure: sealed head `1598c320eeacf452519b8fd7ae8195d928ec74e5` passed fresh governance/security/integration workflows and independent same-head LEAN reproducibility, then merged through PR #18 as `6b08e0cd0bb3536e2f01d88e2bf540d20db54a23`. The accepted head and merge commit share tree `dee4a39e3bc4caf937755768d2ed7278191415ff`; post-merge `qros-gate` passed. Packaging, release, Yuanta integration, live trading, and unpatched upstream runtime remain DENY.

Phase 4 research has identified a minimal Tauri + React SPA + Vite + TypeScript candidate for Windows 11 x64, with system WebView2 Evergreen and Node/Rust/MSVC toolchains. This research does not authorize dependency introduction. TypeScript 7 integration, exact MSVC/WebView2 inventory, and resolved npm/Cargo graphs remain unverified.

Next executable gate: **Phase 4 DESIGN REVIEW**. All Phase 4 dependency-registry entries remain `PLANNED_DENY_USE_UNTIL_PINNED` and introduction remains DENY until a separate implementation candidate produces exact lockfiles, license/security closure, and Windows source-build evidence.

Yuanta, live trading and packaging are independent optional future gates and are not scheduled.
