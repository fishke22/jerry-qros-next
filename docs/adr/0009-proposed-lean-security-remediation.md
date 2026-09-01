# ADR-0009 — Proposed LEAN security-remediation decision

- Status: ACCEPTED RESEARCH DECISION / OPTION A / HARD STOP ACTIVE
- Date: 2026-09-01
- Evidence: Phase 3C exact-pinned NuGet audit
- Approval scope: Option A only; no architecture amendment, source patch, fork, gitlink change, runtime promotion, merge, Phase 4, Yuanta, live trading, packaging, or release authorization

## Finding

The blocking dependency graph reduces to two source boundaries:

1. Compression: DotNetZip 1.16.0 also brings the vulnerable System.Drawing.Common 4.7.0 chain.
2. Messaging: NetMQ 4.0.1.6 brings the vulnerable ServiceModel/WinHttpHandler chain.

The current official LEAN master still contains both root conditions. There is no demonstrated standard-Launcher build that excludes both without changing source/dependency resolution.

## Options

### A — Wait for official LEAN remediation

Keep Phase 3B blocked and periodically re-check official LEAN master/issue #8795. Re-pin only when an official revision has no blocking HIGH/CRITICAL audit result and passes QROS deterministic regression.

**Risk:** delays LEAN-dependent phases.
**Maintenance burden:** lowest.
**Architecture drift:** none.

### B — Authorize a research-only upstream-aligned patch experiment

In a separate non-promotable branch, evaluate:
- complete migration of remaining DotNetZip/Ionic.Zip use to runtime compression; and
- a modern NetMQ dependency or a Messaging-project reduction that removes the obsolete ServiceModel chain.

The experiment would need complete transitive SBOM/license review and the existing Phase 3B deterministic regression plus targeted compression/messaging tests.

**Risk:** creates an effective QROS-maintained LEAN variant.
**Maintenance burden:** high.
**Architecture drift:** yes; explicit approval required before any implementation.

### C — Warning suppression or drop-in DotNetZip fork

REJECT.

## Decision

**Option A is accepted.**

Remain on the current exact LEAN pin and keep the Phase 3 security hard stop active until an official LEAN revision satisfies the established remediation gate and passes independent QROS re-validation.

This acceptance records the selected research disposition only. It does **not** approve an architecture amendment and does **not** authorize Option B, any LEAN source/dependency modification, PR #6 or PR #7 merge, runtime promotion, Phase 4, Yuanta integration, live trading, packaging, or release.

If schedule pressure later justifies Option B, it still requires a separate explicit user architecture authorization before any source/dependency modification.
