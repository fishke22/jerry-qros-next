# ADR-0009 — Proposed LEAN security-remediation decision

- Status: SUPERSEDED BY ADR-0010 / HISTORICAL OPTION A DECISION
- Date: 2026-09-01
- Evidence: Phase 3C exact-pinned NuGet audit
- Historical approval scope: Option A only at the Phase 3C checkpoint
- Superseded: 2026-09-01

## Finding

The blocking dependency graph reduced to two source boundaries:

1. Compression: DotNetZip 1.16.0 also brought the vulnerable System.Drawing.Common 4.7.0 chain.
2. Messaging: NetMQ 4.0.1.6 brought the vulnerable ServiceModel/WinHttpHandler chain.

At the Phase 3C checkpoint, official LEAN master still contained both root conditions and no demonstrated standard-Launcher build excluded both without changing source/dependency resolution.

## Options considered at that checkpoint

### A — Wait for official LEAN remediation

Keep Phase 3B blocked and periodically re-check official LEAN master/issue #8795. Re-pin only when an official revision has no blocking HIGH/CRITICAL audit result and passes QROS deterministic regression.

**Risk:** delays LEAN-dependent phases.
**Maintenance burden:** lowest.
**Architecture drift:** none.

### B — Authorize a research-only upstream-aligned patch experiment

In a separate non-promotable branch, evaluate dependency/source remediation with complete transitive SBOM/license review and deterministic regression.

**Risk:** could create an effective QROS-maintained LEAN variant.
**Maintenance burden:** high.
**Architecture drift:** requires explicit approval.

### C — Warning suppression or unreviewed drop-in fork

REJECT.

## Historical decision

Option A was accepted for the Phase 3C checkpoint. That decision did not authorize an architecture amendment, source patch, fork, gitlink change, runtime promotion, Phase 4, Yuanta integration, live trading, packaging, or release.

## Supersession

A later explicit Phase 3D architecture decision, ADR-0010, superseded Option A after a deterministic checkout-time patch candidate completed full graph, license, CycloneDX, security, build, backtest, semantic-regression, and reproducibility review. The accepted solution does not change the LEAN gitlink or create a fork and is restricted to local Research/Backtest. The unpatched upstream runtime remains denied.
