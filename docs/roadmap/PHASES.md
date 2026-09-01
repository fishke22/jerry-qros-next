# Implementation Roadmap

Execution model: RESEARCH → DESIGN → IMPLEMENT → TEST → REVIEW → ACCEPT/REJECT.

1. Phase 0 — Governance implementation
2. Phase 1 — Repository foundation + versioned contracts
3. Phase 2 — Data receipt / QA / Parquet / DuckDB vertical slice
4. Phase 3 — Pinned LEAN integration — **ACCEPTED / MERGED** for local Research/Backtest only through the deterministic Phase 3D runtime overlay
5. Phase 3E — Post-merge security/provenance hardening — **CURRENT GATE**
6. Phase 4 — QUT Tauri/React zh-TW shell
7. Phase 5 — Research / Backtest / Data QA workspace
8. Phase 6 — Internal AI API + one zero-cost local provider
9. Phase 7 — Mock/Paper Broker + deterministic Safety
10. Phase 8 — Integrated end-to-end verification
11. Phase 9 — Windows CI/local Windows/Norton-Defender/long-run validation
12. PRE-PACKAGING READINESS — HARD STOP

Phase 3 closure: PR #13 integrated the accepted Phase 3B → 3C → 3D stack into `main`. The exact upstream LEAN gitlink remains pinned at `b692bf4788e8b54fc23bdcb5659666bf055ce89f`. The unpatched upstream runtime remains DENY; only `LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH` is allowed.

Next executable gate: **Phase 3E IMPLEMENT → TEST → REVIEW**. Phase 3E closes post-merge P1/P2 findings around exact patched-worktree verification, runtime-bound result/provenance identity, NuGet audit completeness, historical merge-tree verification, and historical Phase 3C denial enforcement. Phase 4 remains blocked until Phase 3E is accepted. All Phase 4 dependencies remain denied until separately researched and pinned.

Yuanta, live trading and packaging are independent optional future gates and are not scheduled.
