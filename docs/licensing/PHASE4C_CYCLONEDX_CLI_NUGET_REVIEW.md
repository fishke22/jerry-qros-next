# Phase 4C — CycloneDX CLI NuGet binary path review

Verified: 2026-09-03

Status: **REJECTED FOR QROS ZERO-COST TOOL ADOPTION**

## Evidence

Exact candidate:
- CycloneDX CLI 0.33.1
- source revision `b3cfa4b0edc356dad07e0b6e7ab6da0a94af0246`
- .NET SDK 10.0.400
- CI-only runtime target `linux-x64`
- nuget.org only
- workflow run `33739454968`, job `100597722306`

The restore/inventory gate itself passed:
- source-evaluation boundary: PASS
- generated lock SHA-256: `01b9d04a2137ddac295892d157e38b2f019c069f799b6db8c90b806aa345add4`
- locked restore: PASS
- unique packages: 18
- direct packages: 7
- base transitive packages: 11
- known NuGet vulnerability gate: PASS
- package license-metadata presence gate: PASS
- CLI build/execution: NOT PERFORMED
- SBOM conversion: NOT PERFORMED

## License/cost blocker

Three transitive packages declare a license file named `OSMFEULA.txt` rather than a simple SPDX expression:

- `Json.More.Net 3.0.1`
- `JsonPointer.Net 7.0.1`
- `JsonSchema.Net 9.3.0`

Their upstream repository is `json-everything/json-everything`.

The repository `LICENSE` is MIT.

However, the upstream `OSMFEULA.txt` separately defines a project-provided **Binary Release** and states that a maintenance fee applies to revenue-generating users with annual gross revenue greater than or equal to US$10,000, subject to listed exemptions. It also states that:
- the source remains under the MIT/OSI license;
- the fee is not a source-code license fee;
- source may be self-compiled without that Binary Release agreement.

Official upstream files:
- https://github.com/json-everything/json-everything/blob/main/LICENSE
- https://github.com/json-everything/json-everything/blob/main/OSMFEULA.txt

QROS does not need to decide whether a particular future user is liable for that fee. The governance rule is simpler:

```text
ZERO_COST_REQUIRED = true
UNKNOWN != ALLOW
UNKNOWN = DENY
```

The tested NuGet path obtains precompiled packages from the package distribution channel. Because the binary-use cost condition is not universally zero-cost, this candidate cannot be adopted by QROS.

## Decision

```text
CYCLONEDX_CLI_SOURCE_LICENSE = Apache-2.0
CYCLONEDX_CLI_NUGET_RESTORE_EVIDENCE = PASS
CYCLONEDX_CLI_NUGET_VULNERABILITY_GATE = PASS
CYCLONEDX_CLI_NUGET_LICENSE_METADATA_PRESENCE = PASS
JSON_EVERYTHING_SOURCE_LICENSE = MIT
JSON_EVERYTHING_PROJECT_BINARY_FEE_CONDITION = PRESENT
CYCLONEDX_CLI_NUGET_BINARY_TOOLCHAIN = REJECT_ZERO_COST
CYCLONEDX_CLI_BUILD = DENY
CYCLONEDX_CLI_EXECUTION = DENY
PHASE4_CANONICAL_SBOM_1_7_PROMOTION = DENY
```

This rejection applies to the tested NuGet binary toolchain. A separately proven source-build route could be researched, but it is not automatically accepted and is not preferred while simpler official OSS alternatives remain available.
