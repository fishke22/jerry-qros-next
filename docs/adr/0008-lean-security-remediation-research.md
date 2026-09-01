# ADR-0008 — Phase 3C LEAN security remediation research boundary

- Status: ACCEPTED HISTORICAL RESEARCH BOUNDARY / SUPERSEDED FOR CURRENT RUNTIME AUTHORITY BY ADR-0010
- Date: 2026-09-01
- Parent: ADR-0007

## Context

Phase 3B proved deterministic QROS-owned synthetic backtesting but was blocked by known HIGH/CRITICAL packages in the exact pinned LEAN dependency graph.

## Decision at Phase 3C

Phase 3C was a research-only gate.

Allowed:
- inspect official LEAN master, issues and merged/closed PRs;
- audit the exact pinned NuGet dependency graph on standard public GitHub-hosted runners;
- evaluate upstream-aligned remediation candidates;
- create evidence, tests and proposed amendments.

Denied at that checkpoint:
- changing `external/lean` gitlink;
- patching or forking LEAN source;
- replacing NuGet dependencies;
- suppressing security advisories;
- upgrading QROS .NET toolchain;
- runtime promotion, packaging, Yuanta or live trading.

The preferred path was a future official LEAN revision with blockers removed. If that was not available, any QROS-maintained patch required a separate architecture amendment and full quant-engine regression before implementation.

## Acceptance

This research gate was accepted when the transitive dependency origins were reproducibly mapped and a remediation proposal could be evaluated without weakening any security or cost invariant. Acceptance of Phase 3C research did not by itself authorize LEAN runtime promotion.

## Supersession note

The statements above remain the historical Phase 3C boundary. ADR-0010 was subsequently approved and is the current runtime authority. It authorizes only the deterministic Phase 3D checkout-time patched local Research/Backtest runtime; it does not authorize a fork, gitlink change, packaging, release, Yuanta integration, or live trading.
