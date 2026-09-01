from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PINNED="b692bf4788e8b54fc23bdcb5659666bf055ce89f";LATEST_OBSERVED="abeb0a0627ec484b92291c45c3f2553726c26199";ADR_0010="docs/adr/0010-phase-3d-lean-security-patch-candidate.md"
def load():return json.loads((ROOT/"config"/"lean-remediation-research.json").read_text(encoding="utf-8"))
def validate():
 r=load()
 if r.get("record_semantics")!="HISTORICAL_PHASE3C_SNAPSHOT":raise AssertionError("Phase 3C record must be explicitly historical")
 if r.get("superseded_by")!=ADR_0010:raise AssertionError("Phase 3C supersession authority drift")
 if r.get("current_runtime_authority")!="config/lean-security-review.json":raise AssertionError("current LEAN runtime authority drift")
 if r.get("current_runtime_state_encoded_here") is not False:raise AssertionError("historical Phase 3C record must not encode current runtime state")
 if r.get("research_only") is not True:raise AssertionError("historical Phase 3C scope must remain research-only")
 for k in ("architecture_amendment_approved","lean_source_patch_authorized","lean_fork_authorized","lean_gitlink_change_authorized","runtime_promotion_allowed"):
  if r.get(k) is not False:raise AssertionError("historical Phase 3C field changed: "+k)
 if r.get("pinned_lean_revision")!=PINNED:raise AssertionError("pinned LEAN revision drift")
 u=r.get("upstream",{})
 if u.get("latest_master_revision")!=LATEST_OBSERVED or u.get("latest_master_dotnetzip_version")!="1.16.0" or u.get("official_revision_remediation_available") is not False:raise AssertionError("Phase 3C upstream observation drift")
 if u.get("issue_8795",{}).get("state")!="OPEN":raise AssertionError("Phase 3C issue #8795 evidence drift")
 c={x["candidate"]:x for x in r.get("candidate_paths",[])}
 for x in ("DROP_IN_DOTNETZIP_FORK","SUPPRESS_NUGET_SECURITY_WARNINGS"):
  if c.get(x,{}).get("status")!="REJECTED":raise AssertionError(x+" historical rejection drift")
 g=r.get("next_gate",{})
 if g.get("historical_phase3c_gate") is not True or g.get("current_runtime_gate") is not False:raise AssertionError("Phase 3C gate chronology drift")
 if g.get("research_evidence_accepted") is not True or g.get("security_remediation_available") is not False or g.get("hard_stop_active") is not True or g.get("architecture_amendment_approved") is not False or g.get("runtime_promotion_allowed") is not False:raise AssertionError("Phase 3C historical gate evidence drift")
 return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--require-remediation",action="store_true");a=p.parse_args();r=validate();print("QROS Phase 3C historical research-snapshot validation: PASS")
 if a.require_remediation and not r["next_gate"]["security_remediation_available"]:print("QROS Phase 3C historical remediation gate: BLOCKED_AT_CHECKPOINT",file=sys.stderr);return 2
 return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except AssertionError as e:print("QROS Phase 3C historical research-snapshot validation: FAIL:",e,file=sys.stderr);raise SystemExit(1)
