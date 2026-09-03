# Phase 4C — Python SBOM library license and zero-cost review

Verified: 2026-09-03

Status: **PASS FOR HASH-LOCKED CANDIDATE INSTALL TEST ONLY**

This review applies only to the exact 26-wheel graph locked by:

- `requirements/candidates/phase4c-cyclonedx-python.lock`
- lock SHA-256: `bd9df0ad87b54e5bb0d03e25572ac23d02d4fd41acc35631dad4b67b61b0dee1`
- wheel inventory SHA-256: `d8e12dffcb25026a2ff493deca400880b7a2aa4111a2b6baf6790e6de7b98d3a`
- PyPI exact-release security evidence SHA-256: `16aa7c55f7eb40dccf930927354ea021574611cc4630a01467fd81a6c8579695`

It does **not** authorize permanent dependency adoption, QROS runtime promotion, canonical CycloneDX 1.7 promotion, packaging, release, Yuanta integration or live trading.

## Review method

Primary evidence is the exact downloaded wheel `METADATA` recorded in:

`docs/source-evidence/phase-4c-python-wheel-inventory.json`

Where artifact metadata was ambiguous, official package/project documentation was used to resolve the ambiguity. No package code was installed or imported during the evidence run.

## Exact license dispositions

| Package | Version | Normalized license | Candidate disposition |
|---|---:|---|---|
| arrow | 1.4.0 | Apache-2.0 | ALLOW candidate install test |
| attrs | 26.1.0 | MIT | ALLOW candidate install test |
| boolean.py | 5.0 | BSD-2-Clause | ALLOW candidate install test |
| cyclonedx-python-lib | 11.12.0 | Apache-2.0 | ALLOW candidate install test |
| defusedxml | 0.7.1 | PSF-2.0 | ALLOW candidate install test |
| fqdn | 1.5.1 | MPL-2.0 | ALLOW CI candidate use; external distribution requires MPL review |
| idna | 3.19 | BSD-3-Clause | ALLOW candidate install test |
| isoduration | 20.11.0 | ISC | ALLOW candidate install test |
| jsonpointer | 3.1.1 | BSD-3-Clause | ALLOW candidate install test |
| jsonschema | 4.26.0 | MIT | ALLOW candidate install test |
| jsonschema-specifications | 2025.9.1 | MIT | ALLOW candidate install test |
| lark | 1.3.1 | MIT | ALLOW candidate install test |
| license-expression | 30.4.4 | Apache-2.0 | ALLOW candidate install test |
| packageurl-python | 0.17.6 | MIT | ALLOW candidate install test |
| py-serializable | 2.1.0 | Apache-2.0 | ALLOW candidate install test |
| python-dateutil | 2.9.0.post0 | BSD-3-Clause | ALLOW candidate install test |
| referencing | 0.37.0 | MIT | ALLOW candidate install test |
| rfc3339-validator | 0.1.4 | MIT | ALLOW candidate install test |
| rfc3986-validator | 0.1.1 | MIT | ALLOW candidate install test |
| rfc3987-syntax | 1.1.0 | MIT | ALLOW candidate install test; stale classifier recorded |
| rpds-py | 2026.6.3 | MIT | ALLOW candidate install test |
| six | 1.17.0 | MIT | ALLOW candidate install test |
| sortedcontainers | 2.4.0 | Apache-2.0 | ALLOW candidate install test |
| tzdata | 2026.3 | Apache-2.0 | ALLOW candidate install test |
| uri-template | 1.3.0 | MIT | ALLOW candidate install test |
| webcolors | 25.10.0 | BSD-3-Clause | ALLOW candidate install test |

## Special case: fqdn / MPL-2.0

The exact `fqdn 1.5.1` package identifies MPL-2.0.

Mozilla describes MPL 2.0 as file-level copyleft. External executable/library distribution requires the MPL-covered source to remain available and recipients to be informed how to obtain it. A larger work may remain under other terms for files that are not MPL-covered.

Current QROS use is only a CI research-tool candidate. No installer, release artifact or external redistribution is authorized. Therefore the current candidate install/test does not require changing unrelated QROS source licenses.

Future package/release review must explicitly handle MPL source/notice obligations if `fqdn` is ever included in a distributed artifact.

Official evidence:
- https://pypi.org/project/fqdn/1.5.1/
- https://github.com/ypcrts/fqdn
- https://www.mozilla.org/en-US/MPL/2.0/FAQ/

## Special case: rfc3987-syntax metadata mismatch

The exact wheel reports:

```text
License-Expression: MIT
legacy classifier: OSI Approved :: Apache Software License
```

Python Packaging core metadata defines `License-Expression` as the SPDX expression applying to the distribution archive and deprecates `License ::` classifiers as of Metadata 2.4.

The exact PyPI 1.1.0 project page also states that the project is MIT licensed.

QROS therefore records:

```text
RFC3987_SYNTAX_1_1_0 = MIT
LEGACY_APACHE_CLASSIFIER = STALE_METADATA_RECORDED
```

Official evidence:
- https://pypi.org/project/rfc3987-syntax/1.1.0/
- https://packaging.python.org/en/latest/specifications/core-metadata/

## Special case: python-dateutil

The official project states that contributions before 2017-12-01 are BSD-3-Clause only, while later contributions are available under Apache-2.0 or BSD-3-Clause.

For a conservative whole-distribution disposition, QROS uses BSD-3-Clause.

Official evidence:
- https://pypi.org/project/python-dateutil/2.9.0.post0/

## Special case: isoduration

The wheel's free-text `License` field is `UNKNOWN`, but the exact PyPI release metadata and classifier identify ISC License.

QROS normalizes this candidate artifact as ISC and records the metadata discrepancy.

Official evidence:
- https://pypi.org/project/isoduration/20.11.0/
- https://github.com/bolsote/isoduration

## Cost review

No project-specific mandatory usage fee condition analogous to the rejected json-everything NuGet binary route was identified in this exact wheel graph.

The normalized licenses are:
- Apache-2.0
- MIT
- BSD-2-Clause
- BSD-3-Clause
- PSF-2.0
- MPL-2.0
- ISC

The candidate therefore satisfies the QROS zero-cost gate for **hash-locked CI install/testing only**.

This is not a claim that future versions or a future distribution bundle have the same status. Revalidation is mandatory on any lock change.

## Decision

```text
EXACT_WHEEL_COUNT = 26
UNKNOWN_NORMALIZED_LICENSE = 0
CONDITIONAL_USAGE_FEE_BLOCKER = 0
STRONG_COPYLEFT = 0
MPL_FILE_LEVEL_COPYLEFT = 1

PHASE4C_PYTHON_LICENSE_GATE = PASS_FOR_CANDIDATE_INSTALL_TEST_ONLY
PHASE4C_PYTHON_ZERO_COST_GATE = PASS_FOR_CANDIDATE_INSTALL_TEST_ONLY

PERMANENT_TOOL_ADOPTION = DENY_PENDING_EXECUTION_AND_FIDELITY_REVIEW
DEPENDENCY_REGISTRY_PROMOTION = DENY
CANONICAL_SBOM_1_7_PROMOTION = DENY
EXTERNAL_DISTRIBUTION = DENY_BY_HARD_GATE
PACKAGE_AUTHORIZED = false
RELEASE_AUTHORIZED = false
```
