# Phase 4 QUT transitive license review

Date: 2026-09-02

Status: CANDIDATE REVIEW / NOT DEPENDENCY ADOPTION / NOT DISTRIBUTION AUTHORIZATION

Scope: the exact Phase 4 implementation-candidate locks on PR #26 for Windows target `x86_64-pc-windows-msvc`.

## Evidence boundary

This review is based on the exact committed `package-lock.json`, exact committed `Cargo.lock`, Windows-target Cargo metadata, npm CycloneDX output, Cargo CycloneDX output, and official license terms. It does not authorize packaging or release.

Hard gates remain:

- `PACKAGE_AUTHORIZED=false`
- `RELEASE_AUTHORIZED=false`
- `YUANTA_INTEGRATION_AUTHORIZED=false`
- `LIVE_TRADING_AUTHORIZED=false`

## npm graph

The exact npm lock contains 81 packages with license metadata present for every package checked by CI.

Observed license summary on the accepted candidate run:

- Apache-2.0: 22
- Apache-2.0 OR MIT: 13
- BSD-3-Clause: 1
- ISC: 1
- MIT: 32
- MPL-2.0: 12

The MPL-2.0 npm entries are `lightningcss 1.33.0` plus its optional platform binaries. They are development/build dependencies of the Vite/Rolldown toolchain. The Windows x64 optional binary is `lightningcss-win32-x64-msvc 1.33.0`.

QROS Phase 4 does not ship `node_modules` and Node/npm/Vite remain build/dev-only. A future package/release review must independently verify that no build-tool executable is accidentally redistributed.

## Windows-target Cargo graph

The Windows-target Cargo graph contains 253 source packages with license metadata present for every package checked by CI.

Exact MPL-2.0 components identified by the reproducible Cargo CycloneDX evidence:

- `cssparser-macros 0.6.1`
- `cssparser 0.36.0`
- `dtoa-short 0.3.5`
- `option-ext 0.2.0`
- `selectors 0.36.1`

These are transitive components in the Tauri/Wry Windows-target dependency graph.

## MPL-2.0 disposition

Mozilla's official MPL 2.0 FAQ states that MPL software may be used by individuals and companies for any purpose. MPL obligations become relevant when covered software is distributed outside the organization. MPL is file-level copyleft, not a requirement to relicense unrelated new QROS files.

For executable distribution, MPL 2.0 Section 3.2 requires the covered source to be made available and recipients to be informed how to obtain it. A Larger Work may be distributed under terms of the distributor's choice while the MPL requirements continue to apply to the covered software.

QROS disposition:

- current source-build/testing use: `ALLOW_WITH_LICENSE_RECORD`
- commercial use: `ALLOW`
- QROS proprietary/unrelated source forced to MPL: `NO`
- future external executable distribution: `REQUIRES_MPL_SOURCE_AND_NOTICE_COMPLIANCE_REVIEW`
- current packaging/release: `DENY_BY_HARD_GATE`

No QROS modification to these MPL packages is currently recorded. If future work modifies MPL-covered files, that modification must receive a new license review before distribution.

Official evidence:

- Mozilla MPL 2.0 FAQ: use for any purpose; distribution obligations; file-level copyleft.
- Mozilla Public License 2.0 Sections 3.1-3.4: source/executable/larger-work distribution and notices.

## Cargo CycloneDX evidence tool

Candidate CI used `cargo-cyclonedx 0.5.9`, an Apache-2.0 OWASP CycloneDX Rust project, as an ephemeral build/research tool only. It is not a QROS runtime dependency.

The exact install log reports that the tool's own locked dependency graph contains yanked `xml-rs 0.8.19`. Yanked status does not itself establish a QROS runtime vulnerability, and the package is not part of the generated QROS dependency graph. However, under QROS fail-closed governance this prevents silently promoting `cargo-cyclonedx` to a permanent accepted tool without a separate tool-supply-chain review or replacement.

Disposition:

`CARGO_CYCLONEDX_0_5_9 = ALLOW_FOR_CANDIDATE_EVIDENCE_ONLY / PERMANENT_TOOL_ADOPTION_DEFERRED`

## Decision

The transitive license set found so far does not establish a zero-cost or commercial-use blocker for the Phase 4 source-build candidate.

This is not final release-license closure because packaging and external distribution are not authorized and the eventual distributed file set does not yet exist.

`PHASE4_SOURCE_BUILD_LICENSE_GATE = PASS_WITH_RECORDED_MPL_OBLIGATIONS`

`PHASE4_RELEASE_LICENSE_GATE = NOT_EVALUATED / DENY`
