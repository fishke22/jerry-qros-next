from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"packages"/"contracts"/"contract-manifest.json"

def fail(message:str)->None:
    raise AssertionError(message)

def load(path:Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def validate_manifest()->None:
    manifest=load(MANIFEST)
    if manifest.get("manifest_version")!=1:
        fail("contract manifest version must be 1")
    if manifest.get("unknown_is_deny") is not True:
        fail("contract manifest must remain fail-closed")
    ids=set()
    for item in manifest.get("contracts",[]):
        key=(item.get("contract_id"),item.get("version"))
        if key in ids:
            fail(f"duplicate contract/version: {key}")
        ids.add(key)
        schema=ROOT/item["schema_path"]
        if not schema.exists():
            fail(f"missing schema: {schema.relative_to(ROOT)}")
        doc=load(schema)
        expected=f"/{item['contract_id']}/v{item['version']}"
        if expected not in doc.get("$id",""):
            fail(f"schema id/version mismatch: {schema.relative_to(ROOT)}")
        if doc.get("type")!="object":
            fail(f"contract root must be object: {schema.relative_to(ROOT)}")
        if doc.get("additionalProperties") is not False:
            fail(f"contract must reject unknown fields: {schema.relative_to(ROOT)}")

def validate_local_promotion_policy()->None:
    p=load(ROOT/"config"/"local-source-promotion-policy.json")
    if p.get("unknown_is_deny") is not True:
        fail("local source promotion must be fail-closed")
    q=p["source_boundaries"]["legacy_qros_local"]
    if q.get("whole_repository_upload_allowed") is not False or q.get("git_history_import_allowed") is not False:
        fail("legacy QROS whole-repo/history upload must remain denied")
    y=p["source_boundaries"]["yuanta_autopilot_local"]
    if y.get("access_mode")!="DENY" or y.get("inspection_allowed") is not False or y.get("upload_allowed") is not False:
        fail("Yuanta local boundary was weakened")

def validate_semantic_invariants()->None:
    good=load(ROOT/"tests"/"fixtures"/"contracts"/"data-receipt.pass.v1.json")
    unknown=load(ROOT/"tests"/"fixtures"/"contracts"/"data-receipt.unknown.v1.json")
    passed=load(ROOT/"tests"/"fixtures"/"contracts"/"validation-result.pass-review-only.v1.json")
    blocked=load(ROOT/"tests"/"fixtures"/"contracts"/"validation-result.blocked.v1.json")
    required={"source_timestamp","first_known_timestamp","received_at","source_hash","normalizer_version","validator_version","quality_status"}
    if not required.issubset(good):
        fail("data receipt missing authoritative provenance fields")
    if good["quality_status"]=="PASS" and (good["source_timestamp"] is None or good["first_known_timestamp"] is None):
        fail("PASS receipt cannot have unknown critical timestamps")
    if unknown["quality_status"]!="UNKNOWN" or unknown["source_timestamp"] is not None:
        fail("unknown receipt fixture must remain explicit")
    for result in (passed,blocked):
        if result["gate_opened"] is not False or result["research_only"] is not True:
            fail("validation result may not auto-open a gate")
    if passed["classification"]!="PASS_REVIEW_ONLY" or passed["blocking_reasons"]:
        fail("PASS_REVIEW_ONLY fixture drift")
    if blocked["classification"]!="BLOCKED_INSUFFICIENT_EVIDENCE" or not blocked["blocking_reasons"]:
        fail("blocked fixture drift")

def main()->int:
    for fn in (validate_manifest,validate_local_promotion_policy,validate_semantic_invariants):
        fn();print("PASS",fn.__name__)
    print("QROS Phase 1 contract gate: PASS")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except AssertionError as exc:
        print("QROS Phase 1 contract gate: FAIL:",exc)
        raise SystemExit(1)
