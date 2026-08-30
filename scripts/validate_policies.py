from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
"zero_cost_required":True,"paid_services_allowed":False,"paid_runners_allowed":False,
"larger_runners_allowed":False,"gpu_runners_allowed":False,"paid_data_allowed":False,
"paid_llm_api_allowed":False,"paid_storage_allowed":False,"paid_code_signing_allowed":False,
"actions_paid_overage_allowed":False,"package_authorized":False,"release_authorized":False,
"yuanta_integration_authorized":False,"live_trading_authorized":False,"repository_visibility":"public"}
SOURCE_FIELDS={"source_id","provider","dataset","endpoint","official_status","cost_class","access_class","data_role","historical_depth","frequency","latency","storage_rights","redistribution_rights","terms_url","terms_verified_at","provenance_required","validation_grade","fallback_source","status"}
FORBIDDEN_SUFFIXES={".pfx",".p12",".pem",".key",".jks",".kdbx"}
FORBIDDEN_PATH_MARKERS={"yuanta-sdk","spark-sdk","broker-private","credentials","certificates"}
SECRET_PATTERNS={
"github_token":re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
"openai_key":re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
"aws_access_key":re.compile(r"AKIA[0-9A-Z]{16}"),
"private_key_header":re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")}
FORBIDDEN_WORKFLOW_TERMS=("gh release create","tauri build","nsis","msix","larger-runner","gpu-runner")
ACTION_RE=re.compile(r"^\s*-\s*uses:\s*[^@\s]+@([^\s#]+)",re.MULTILINE)
FULL_SHA_RE=re.compile(r"^[0-9a-f]{40}$")
def fail(m): raise AssertionError(m)
def load(p):
 with p.open(encoding="utf-8") as f:return json.load(f)
def validate_cost():
 p=load(ROOT/"config"/"cost-policy.json")
 if p.get("policy_version")!=1:fail("cost policy_version must remain 1")
 for k,v in EXPECTED.items():
  if p.get(k)!=v:fail(f"hard gate changed: {k}={p.get(k)!r}, expected {v!r}")
 if p.get("artifact_retention_days_max",999)>7:fail("artifact retention > 7 days")
def validate_sources():
 r=load(ROOT/"config"/"data-source-registry.json")
 if r.get("registry_version")!=1 or r.get("policy",{}).get("unknown_is_deny") is not True:fail("registry must remain v1 fail-closed")
 if r.get("constraints",{}).get("JNU_VALIDATION_GRADE_INTRADAY")!="UNSOLVED_UNDER_ZERO_COST_POLICY":fail("JNU validation-grade intraday gate changed")
 for s in r.get("sources",[]):
  m=SOURCE_FIELDS-set(s)
  if m:fail(f"{s.get('source_id')} missing {sorted(m)}")
  if s["provenance_required"] is not True:fail(f"{s['source_id']} provenance_required must be true")
  if s["terms_verified_at"] is None and not s["status"].startswith("DENY_"):fail(f"{s['source_id']} unknown terms must deny ingestion")
def files():
 ignore={".git","__pycache__",".pytest_cache","node_modules","target","dist","build"}
 for p in ROOT.rglob("*"):
  if p.is_file():
   rel=p.relative_to(ROOT)
   if not any(x in ignore for x in rel.parts):yield p,rel
def validate_secrets():
 hits=[]
 for p,rel in files():
  parts={x.lower() for x in rel.parts}
  if p.suffix.lower() in FORBIDDEN_SUFFIXES:hits.append(f"forbidden file {rel}");continue
  if FORBIDDEN_PATH_MARKERS&parts:hits.append(f"forbidden private path {rel}");continue
  try:t=p.read_text(encoding="utf-8")
  except UnicodeDecodeError:continue
  for n,rx in SECRET_PATTERNS.items():
   if rx.search(t):hits.append(f"possible {n}: {rel}")
 if hits:fail("; ".join(hits))
def validate_workflows():
 d=ROOT/".github"/"workflows"
 w=list(d.glob("*.yml"))+list(d.glob("*.yaml"))
 if not w:fail("governance workflow required")
 for p in w:
  t=p.read_text(encoding="utf-8");low=t.lower()
  if any(x in low for x in FORBIDDEN_WORKFLOW_TERMS):fail(f"forbidden workflow term in {p.relative_to(ROOT)}")
  if "runs-on:" in low and not any(x in low for x in ("ubuntu-latest","ubuntu-24.04","windows-latest","windows-2025","windows-2022")):fail(f"unapproved runner in {p.relative_to(ROOT)}")
  for ref in ACTION_RE.findall(t):
   if not FULL_SHA_RE.fullmatch(ref):fail(f"action not pinned to full SHA in {p.relative_to(ROOT)}: @{ref}")
  if p.name.lower().startswith(("package","release")):fail("package/release workflow forbidden")
def main():
 for fn in (validate_cost,validate_sources,validate_secrets,validate_workflows):
  fn();print("PASS",fn.__name__)
 print("QROS Phase 0 policy gate: PASS");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except AssertionError as e:
  print("QROS Phase 0 policy gate: FAIL:",e,file=sys.stderr);raise SystemExit(1)
