# ADR-0009 — Proposed LEAN security-remediation decision

- Status: PROPOSED / NOT APPROVED
- Date: 2026-09-01
- Evidence: Phase 3C exact-pinned NuGet audit

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

## Proposed decision

Default to **Option A**. Do not create a QROS LEAN fork/patch while upstream is actively migrating compression and a current official secure revision may become available.

If schedule pressure justifies Option B, it requires an explicit user architecture authorization before any source/dependency modification.

This ADR does not itself authorize Option B.
