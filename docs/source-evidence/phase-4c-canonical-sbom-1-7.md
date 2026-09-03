# Phase 4C — Canonical CycloneDX 1.7 research

Verified: 2026-09-03

Status: **RESEARCH / DESIGN CANDIDATE ONLY**

Issue: #27

## Problem

QROS canonical supply-chain policy requires CycloneDX 1.7. The Phase 4 Cargo candidate currently produces deterministic CycloneDX 1.5 evidence.

This is a promotion blocker, not a reason to discard the 1.5 candidate evidence.

```text
PHASE4_CARGO_SBOM_1_5_CANDIDATE_EVIDENCE = ALLOW_FOR_CANDIDATE_REVIEW_ONLY
PHASE4_CANONICAL_SBOM_1_7_PROMOTION = DENY
```

## Verified official evidence

### CycloneDX specification

Official CycloneDX states that CycloneDX is ECMA-424, the JSON Schema is the reference implementation, schemas are Apache-2.0, and CycloneDX 1.7 was released on 2025-10-21.

Official repository:
- https://github.com/CycloneDX/specification
- https://github.com/CycloneDX/specification/releases/tag/1.7

A later 1.7.1 schema-alignment/fix commit is:
- `b29bae660048e0ad2fbc5f2972927b442ce951c4`

### cargo-cyclonedx

Current accepted Phase 4 candidate uses:
- cargo-cyclonedx 0.5.9
- deterministic `SOURCE_DATE_EPOCH`
- Windows target `x86_64-pc-windows-msvc`
- CycloneDX 1.5
- 253 components
- SBOM SHA-256 `50e315c02680106ff3004e6e194f58d4cbbd8732fab33aff08ff122972da3623`

Official changelog:
- https://github.com/CycloneDX/cyclonedx-rust-cargo/blob/main/cargo-cyclonedx/CHANGELOG.md

Upstream PR #875 to add 1.6/1.7 support was still open when verified:
- https://github.com/CycloneDX/cyclonedx-rust-cargo/pull/875

Therefore native 1.7 generation is not currently an accepted available path.

### CycloneDX CLI

CycloneDX CLI 0.30.0 added 1.7 support. Current release 0.33.1 was released 2026-07-23.

Exact 0.33.1 source revision:
- `b3cfa4b0edc356dad07e0b6e7ab6da0a94af0246`

Official source and license:
- https://github.com/CycloneDX/cyclonedx-cli
- Apache-2.0

The CLI supports:
- JSON input/output
- `convert --output-version v1_7`
- `validate --input-version v1_7 --fail-on-errors`

The 0.33.1 source project targets `net10.0`.

Important reproducibility finding: the searched upstream tree does not provide a `packages.lock.json`. Exact top-level PackageReference versions alone are not sufficient QROS transitive-lock evidence.

### .NET toolchain

As of verification, Microsoft lists .NET 10.0.11 as the current 10.0 security patch line and SDK 10.0.400 as a current SDK carrying it.

Official:
- https://dotnet.microsoft.com/download/dotnet/10.0
- https://github.com/dotnet/core/blob/main/release-notes/10.0/10.0.11/10.0.11.md

Microsoft documents `packages.lock.json` and `dotnet restore --locked-mode` / `RestoreLockedMode` for repeatable restore:
- https://learn.microsoft.com/dotnet/core/tools/dotnet-restore
- https://learn.microsoft.com/dotnet/core/install/upgrade

.NET source is MIT. Windows product distributions have a separate .NET product-distribution license boundary:
- https://github.com/dotnet/runtime/blob/main/LICENSE.TXT
- https://github.com/dotnet/core/blob/main/license-information.md

## Candidate architecture

```text
locked Cargo graph
  -> cargo-cyclonedx 0.5.9
  -> deterministic CycloneDX 1.5 JSON
  -> exact CycloneDX CLI 0.33.1 source revision
  -> exact .NET SDK 10.0.400
  -> QROS-reviewed packages.lock.json + locked restore
  -> JSON-to-JSON convert to CycloneDX 1.7
  -> CLI/schema validation
  -> QROS semantic fidelity comparison
  -> provenance/hash/license evidence
```

This is a candidate design only. It does not authorize tool adoption.

## Fidelity gate

Schema-valid output is necessary but insufficient.

The conversion must preserve or explicitly explain every QROS-required semantic element. At minimum compare:

- metadata component identity
- component count
- unique `bom-ref`
- name/version
- purl
- hashes
- license representation
- dependency references
- dependency edge set

Any unexplained loss, mutation, duplicate identity, or graph change fails closed.

Upstream has open conversion/interoperability issues for some format paths, especially SPDX conversions. Those issues do not prove CycloneDX 1.5→1.7 data loss, but they are evidence that QROS must verify fidelity rather than assume it.

## Rejected / deferred paths

### Manual `specVersion` rewrite

REJECT. Changing only the version string does not prove 1.7 schema or semantic compliance.

### Unverified prebuilt binary

REJECT for this candidate. QROS avoids download-and-execute without a complete artifact provenance/checksum/attestation review.

### Docker required path

REJECT. Adds unnecessary runtime/tooling boundary for a local/static transformation.

### Wait only for upstream PR #875

DEFERRED OPTION. If upstream releases native 1.7 before QROS closes this gate, re-evaluate. QROS should not block all current research on an unmerged upstream PR.

## Decision

```text
PHASE4_CANONICAL_SBOM_1_7_RESEARCH = PASS
PHASE4_CANONICAL_SBOM_1_7_DESIGN_CANDIDATE = ACCEPT_FOR_REVIEW
PHASE4_CANONICAL_SBOM_1_7_IMPLEMENTATION = NOT_AUTHORIZED
CYCLONEDX_CLI_PERMANENT_ADOPTION = DENY
DEPENDENCY_ADOPTION = DENY
MAIN_RUNTIME_PROMOTION = DENY
PRODUCTION_READINESS = DENY
```

Hard gates remain unchanged.
