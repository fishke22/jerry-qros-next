# ADR-0008 — Phase 3C LEAN security remediation research boundary

- Status: RESEARCH / NO ARCHITECTURE AMENDMENT APPROVED
- Date: 2026-09-01
- Parent: ADR-0007

## Context

Phase 3B proved deterministic QROS-owned synthetic backtesting but was blocked by known HIGH/CRITICAL packages in the exact pinned LEAN dependency graph.

## Decision

Phase 3C is a research-only gate.

Allowed:
- inspect official LEAN master, issues and merged/closed PRs;
- audit the exact pinned NuGet dependency graph on standard public GitHub-hosted runners;
- evaluate upstream-aligned remediation candidates;
- create evidence, tests and proposed amendments.

Denied:
- changing `external/lean` gitlink;
- patching or forking LEAN source;
- replacing NuGet dependencies;
- suppressing security advisories;
- upgrading QROS .NET toolchain;
- runtime promotion, packaging, Yuanta or live trading.

The preferred path is a future official LEAN revision with blockers removed. If that is not available, any QROS-maintained patch requires a separate architecture amendment and full quant-engine regression before implementation.

## Acceptance

This research gate is accepted when the transitive dependency origins are reproducibly mapped and a remediation proposal can be evaluated without weakening any security or cost invariant. Acceptance of Phase 3C research does not authorize Phase 3B merge or LEAN runtime promotion.
