# Phase 4C — Python install/import compatibility candidate

Verified parent evidence: 2026-09-03

Status: **IMPLEMENTATION CANDIDATE / INSTALL + IMPORT ONLY**

Parent research:
- PR #30
- exact parent head: `336f4b3eacd70d3ab2ac1392fe5e58463fae9c20`
- qros-gate #187: SUCCESS
- Python wheel research #10: SUCCESS
- exact 26-wheel license gate: PASS for candidate install test only
- zero-cost gate: PASS for candidate install test only

## Purpose

This gate answers only:

1. Can the exact 26-wheel graph be installed into an isolated Python 3.14.7 venv without resolving or building anything new?
2. Does the installed graph match the exact candidate lock?
3. Can the required CycloneDX Python APIs be imported without using the QROS repository as cwd, without ambient environment variables, and with ordinary socket/subprocess operations denied?
4. Are the expected API symbols present?

It does **not** call:
- `Bom.from_json(...)`
- `JsonV1Dot7(...)`
- JSON schema validation
- any QROS SBOM conversion

## Installation controls

The workflow must:
- download only exact hash-locked wheels;
- reject non-wheel artifacts;
- reject any `.pth` files;
- reject all unlisted wheel `.data/scripts/` payloads;\n- allow only `jsonpointer-3.1.1.data/scripts/jsonpointer` when its SHA-256 is exactly `4c9bda8829e436ce6c732194421f645240695bf647a75eb210f17256215f7b22`;
- create a dedicated venv;
- install with `--no-index --no-deps --require-hashes`;
- run `pip check`;
- compare installed distribution names and versions against the 26-entry lock.

`entry_points.txt` may be inventoried, but entry points are not executed.\n\nThe one allowed wheel data script was reviewed against upstream `stefankoegl/python-json-pointer` release commit `5998f951dcc5ace60f67f35afe6778c445401a07`, path `bin/jsonpointer`. It is a command-line JSON Pointer utility. PyPA's Wheel specification defines `.data/scripts/` as files moved to the environment's scripts destination during install; QROS does not execute this script. Upstream source SHA-256 is `0922c792b58faecab05e9010713eb5345b964848abeecd62d901a0f10ff1a0c6`. The wheel-contained script SHA-256 is `4c9bda8829e436ce6c732194421f645240695bf647a75eb210f17256215f7b22`; the byte-level difference is only the first-line normalization from `#!/usr/bin/env python3` to `#!python`, which matches the PyPA Wheel specification for packaged scripts. Any additional script or content-hash drift fails closed.

## Import controls

The import process must:
- run outside the repository working directory;
- use the venv's Python with isolated mode `-I`;
- start from an empty environment;
- set a temporary HOME;
- disable bytecode writes;
- monkeypatch ordinary socket creation/connection to fail;
- monkeypatch subprocess/process-launch helpers to fail;
- import only the specific CycloneDX API modules needed for the next gate.

This is a compatibility test, not a proof against malicious native code. The exact artifact hashes, PyPI security evidence and prior license/supply-chain gates remain prerequisites.

## Decision boundary

```text
HASH_LOCKED_CANDIDATE_INSTALL = AUTHORIZED
LIMITED_API_IMPORT = AUTHORIZED

BOM_FROM_JSON_EXECUTION = DENY
JSON_V1_7_GENERATION = DENY
SCHEMA_VALIDATION_EXECUTION = DENY
SEMANTIC_FIDELITY_TEST = DENY

PERMANENT_TOOL_ADOPTION = DENY
DEPENDENCY_REGISTRY_PROMOTION = DENY
CANONICAL_SBOM_1_7_PROMOTION = DENY
PACKAGE/RELEASE/YUANTA/LIVE = DENY
```


## Observed candidate evidence

Workflow run: `33743936003`  
Job: `100612043832`

```text
QROS_PHASE4C_PTH_GATE = PASS
QROS_PHASE4C_WHEEL_DATA_SCRIPTS_EXACT_ALLOWLIST = PASS
QROS_PHASE4C_ENTRY_POINTS_INVENTORIED = PASS
QROS_PHASE4C_ACTIVATION_SURFACES_SHA256 =
  f38359daa01e72c90c13130ff00e772e377d96c27d8374e85edda696d4ff9ef5

QROS_PHASE4C_HASH_LOCKED_INSTALL = PASS
QROS_PHASE4C_INSTALLED_DISTRIBUTION_SET = PASS
QROS_PHASE4C_INSTALLED_DISTRIBUTION_COUNT = 26

QROS_PHASE4C_CYCLONEDX_VERSION = 11.12.0
QROS_PHASE4C_BOM_FROM_JSON_SYMBOL = PASS
QROS_PHASE4C_JSON_V1_7_SYMBOL = PASS
QROS_PHASE4C_JSON_VALIDATOR_SYMBOLS = PASS
QROS_PHASE4C_LIMITED_IMPORT = PASS

QROS_PHASE4C_BOM_FROM_JSON_EXECUTION = NOT_PERFORMED
QROS_PHASE4C_JSON_V1_7_GENERATION = NOT_PERFORMED
QROS_PHASE4C_SCHEMA_VALIDATION_EXECUTION = NOT_PERFORMED
QROS_PHASE4C_SEMANTIC_FIDELITY_TEST = NOT_PERFORMED
QROS_PHASE4C_CANONICAL_SBOM_1_7_PROMOTION = DENY
```

The successful import smoke was executed outside the repository working directory with an empty environment and ordinary socket/subprocess helpers denied.

This closes only the install/import compatibility gate. The next allowed gate is a separate semantic-fidelity conversion candidate.
