# Phase 4C — Python CycloneDX 1.7 converter candidate research

Verified: 2026-09-03

Status: **RESEARCH / WHEEL-METADATA RESOLUTION ONLY**

## Why this path is being evaluated

The CycloneDX CLI 0.33.1 NuGet binary path was rejected by QROS `ZERO_COST_REQUIRED` after exact transitive-license review found the json-everything project binary maintenance-fee condition.

The next candidate is the official CycloneDX Python Library.

## Official evidence

Candidate:
- package: `cyclonedx-python-lib`
- version: `11.12.0`
- release commit: `52cb3c94f023df887ac65a6125bce4d63ab7857e`
- license: Apache-2.0
- Python: >=3.9,<4
- QROS existing Python toolchain: 3.14.7

PyPI 11.12.0 provides a universal `py3-none-any` wheel with SHA-256:

`0e807521a921a5c3cb8ce1153f8a61d29eedfe76a46aac2796b7c6b573391a54`

PyPI records Trusted Publishing provenance for the wheel.

Official:
- https://pypi.org/project/cyclonedx-python-lib/11.12.0/
- https://github.com/CycloneDX/cyclonedx-python-lib/commit/52cb3c94f023df887ac65a6125bce4d63ab7857e

## Capability evidence from exact source

The exact release source contains:
- documented and tested `Bom.from_json` deserialization;
- real-world tests that deserialize CycloneDX 1.5 JSON;
- `JsonV1Dot7` serialization;
- `JsonValidator` / `JsonStrictValidator` using bundled CycloneDX JSON schemas when the `json-validation` extra is present.

This makes the library materially different from the JavaScript library candidate, whose JSON deserializer remains TODO.

## Declared runtime dependencies

Core:
- `packageurl-python >=0.11,<2`
- `py-serializable ^2.1.0`
- `sortedcontainers ^2.4.0`
- `license-expression ^30`
- `typing_extensions ^4.6` only for Python <3.13, therefore not expected on QROS Python 3.14.7

JSON validation extra:
- `jsonschema ^4.25` with `format-nongpl`
- `referencing >=0.28.4`

The exact resolved graph is intentionally **not assumed** from these ranges. CI must resolve wheel-only artifacts, record exact versions/hashes and inspect each wheel's license metadata before any install/import/execution is authorized.

## Safety boundary

The candidate workflow may:
- use the already-adopted CPython 3.14.7/setup-python path;
- contact only the public PyPI index/files infrastructure;
- use `pip download --only-binary=:all:`;
- inspect wheel ZIP/METADATA content as data;
- generate an exact candidate hash lock;
- re-download exact hashes to prove artifact reproducibility.

It may not:
- install packages;
- import downloaded packages;
- execute package code;
- build an sdist/wheel;
- run a conversion;
- modify QROS runtime dependencies.

## Decision before resolution

```text
PYTHON_CYCLONEDX_LIBRARY_RESEARCH = ALLOW
WHEEL_METADATA_RESOLUTION = ALLOW
PACKAGE_INSTALL = DENY
PACKAGE_IMPORT = DENY
CONVERTER_EXECUTION = DENY
CANONICAL_SBOM_1_7_PROMOTION = DENY
```
