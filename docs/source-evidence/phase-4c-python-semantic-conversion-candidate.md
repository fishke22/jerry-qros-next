# Phase 4C — semantic fidelity conversion candidate

Status: **CANDIDATE TEST ONLY**

This gate combines two reviewed evidence paths without promoting either:
- QUT Cargo SBOM input from PR #26 exact head `32e74ccfde93cf02fc0f149dd84a9c4ea6b1112e`.
- Python converter install/import path from PR #31 exact head `a07c1cde826d3fe0007d51348ef438ac07a3bfc2`.

## Exact input evidence

Latest PR #26 Cargo SBOM evidence:
- workflow run: `33736531658`
- CycloneDX JSON: 1.5
- Cargo.lock SHA-256: `c9abfa64e57be2dd18efa91d8ae4abf43944bdbae75af94555ff28daa7601adb`
- SBOM SHA-256: `50e315c02680106ff3004e6e194f58d4cbbd8732fab33aff08ff122972da3623`
- components: 253

The workflow must regenerate from the exact PR #26 snapshot and fail unless the SHA-256 matches prior evidence byte-for-byte.

`cargo-cyclonedx 0.5.9` stays candidate-evidence input-generator only.

## Conversion and fidelity rule

The exact input is strictly validated as 1.5, deserialized with `Bom.from_json`, serialized with `JsonV1Dot7`, then strictly validated as 1.7.

Two fresh deserializations must produce byte-identical output.

Initial semantic rule is deliberately strict: JSON deep equality after removing only `$schema` and `specVersion`. No other normalization is pre-authorized. Any additional difference fails closed for explicit review.

Conversion runs outside the repo cwd, with temporary HOME, isolated Python mode, and ordinary socket/subprocess helpers denied.

```text
BOM_FROM_JSON_EXECUTION = AUTHORIZED_FOR_CANDIDATE_TEST
JSON_V1_7_GENERATION = AUTHORIZED_FOR_CANDIDATE_TEST
SCHEMA_VALIDATION_EXECUTION = AUTHORIZED_FOR_CANDIDATE_TEST
SEMANTIC_FIDELITY_TEST = AUTHORIZED_FOR_CANDIDATE_TEST

PERMANENT_TOOL_ADOPTION = DENY
CARGO_CYCLONEDX_PERMANENT_ADOPTION = DENY
DEPENDENCY_REGISTRY_PROMOTION = DENY
CANONICAL_SBOM_1_7_PROMOTION = DENY
PACKAGE/RELEASE/YUANTA/LIVE = DENY
```


## Reviewed serialNumber normalization

Diagnostic workflow run `33755577669` (job `100649075398`) reached real conversion and proved:

- strict CycloneDX 1.5 input validation: PASS;
- two raw library outputs differed only in top-level `serialNumber`;
- example generated values were distinct `urn:uuid:...` values;
- exact `cyclonedx-python-lib 11.12.0` source initializes a missing BOM serial number with `uuid4()`;
- the exact bundled CycloneDX 1.7 JSON schema requires only `bomFormat` and `specVersion`; `serialNumber` is recommended but optional.

The canonical candidate therefore uses this narrow rule:

```text
if input contains serialNumber:
    output serialNumber MUST equal input exactly
else:
    raw library output MUST contain a valid urn:uuid serialNumber
    remove only that generated serialNumber from canonical output
```

This does not ignore arbitrary nondeterminism. After the above rule, two fresh conversions must still be byte-identical, strict-valid as CycloneDX 1.7, and semantic-deep-equal to the input after removing only `$schema` and `specVersion`.
