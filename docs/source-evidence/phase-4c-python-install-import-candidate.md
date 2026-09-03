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
- reject wheel `.data/scripts/` payloads;
- create a dedicated venv;
- install with `--no-index --no-deps --require-hashes`;
- run `pip check`;
- compare installed distribution names and versions against the 26-entry lock.

`entry_points.txt` may be inventoried, but entry points are not executed.

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
