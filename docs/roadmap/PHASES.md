# Implementation Roadmap

Execution model: RESEARCH → DESIGN → IMPLEMENT → TEST → REVIEW → ACCEPT/REJECT.

1. Phase 0 — Governance implementation
2. Phase 1 — Repository foundation + versioned contracts
3. Phase 2 — Data receipt / QA / Parquet / DuckDB vertical slice
4. Phase 3 — Pinned LEAN integration — **ACCEPTED / MERGED** for local Research/Backtest only through the deterministic Phase 3D runtime overlay
5. Phase 3E — Post-merge security/provenance hardening — **ACCEPTED / MERGED**
6. Phase 4 — QUT Tauri/React zh-TW shell
7. Phase 5 — Research / Backtest / Data QA workspace
8. Phase 6 — Internal AI API + one zero-cost local provider
9. Phase 7 — Mock/Paper Broker + deterministic Safety
10. Phase 8 — Integrated end-to-end verification
11. Phase 9 — Windows CI/local Windows/Norton-Defender/long-run validation
12. PRE-PACKAGING READINESS — HARD STOP

Phase 3 closure: PR #13 integrated the accepted Phase 3B → 3C → 3D stack into `main`. The exact upstream LEAN gitlink remains pinned at `b692bf4788e8b54fc23bdcb5659666bf055ce89f`. The unpatched upstream runtime remains DENY; only `LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH` is allowed.

Phase 3E closure: PR #15 was accepted at head `968255313ff0bff9051d50d17da335bd9da10207`, reproduced by same-head LEAN jobs `99900913880` and `99901744740`, and squash-merged as `791d99363228126e199d6cdac89857612743a2c9`. Accepted and integration Git trees are identical at `f49978fe60d85c642505e636e72d407ddb9745b5`. Post-merge main qros-gate `33522024604` passed. Runtime authorization remains restricted to the Phase 3D patched local Research/Backtest scope.

Next executable gate: **Phase 4 RESEARCH → DESIGN**. Phase 4 implementation and every new dependency remain DENY until current official source, exact version/revision, license, zero-cost status, Windows 11 x64 suitability, security posture, provenance plan, and pins are independently verified and reviewed.

Yuanta, live trading and packaging are independent optional future gates and are not scheduled.
