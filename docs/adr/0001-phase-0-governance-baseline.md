# ADR-0001 — Phase 0 Governance Baseline

- Status: ACCEPTED
- Date: 2026-08-31
- Authority: `deep-research-report.md` + current user-approved public-repository amendment

## Decision
Establish policy JSON, source registry, security/build/test/dependency policies, versioned schema placeholders, stdlib-only policy validation and a minimal Ubuntu standard-runner CI gate.

This records implementation of existing authority; it does not amend architecture.

## Consequences
Ordinary development cannot silently flip hard gates. Unknown dependency licenses/data rights remain denied. Phase 0 introduces no QROS runtime dependency. Architecture changes still require Evidence → ADR → Proposed Amendment → Tests → user approval.
