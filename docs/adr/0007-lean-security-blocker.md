# ADR-0007 — Block LEAN runtime promotion on known vulnerable dependencies

- Status: PROPOSED_AMENDMENT_SECURITY_BLOCKER
- Date: 2026-08-31
- Scope: Phase 3B and later LEAN runtime promotion

## Evidence

The exact pinned LEAN revision `b692bf4788e8b54fc23bdcb5659666bf055ce89f` builds and executes the QROS-owned deterministic synthetic backtest successfully. The same exact build reports known HIGH and CRITICAL NuGet vulnerabilities in the dependency graph.

The most severe blockers include DotNetZip 1.16.0 (GHSA-xhg6-9j5j-w4vf, no patched DotNetZip release) and System.Drawing.Common 4.7.0 (GHSA-rxg9-xrhp-64gj, patched in 4.7.2). Additional HIGH warnings occur in Messaging dependencies.

## Decision

1. Keep QuantConnect LEAN as the selected canonical quant-engine architecture candidate.
2. Do not promote the current pinned LEAN build into an accepted QROS runtime while any known HIGH/CRITICAL dependency blocker remains.
3. Do not silently override NuGet versions, modify the gitlink, or create a QROS fork. Any such remediation changes the reviewed engine build and requires a separate architecture amendment plus quant regression.
4. Phase 3B functional evidence may be retained as research evidence, but `PASS_REVIEW_ONLY` never opens a runtime or trading gate.
5. Require a full transitive NuGet SBOM/audit before future runtime promotion.

## Consequence

Phase 3B is blocked at SECURITY REVIEW despite successful deterministic backtesting. PR #6 remains unmerged. The next engineering gate is LEAN dependency remediation research, not further execution or brokerage integration.
