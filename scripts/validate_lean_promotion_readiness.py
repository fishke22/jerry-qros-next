from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load():
    return json.loads((ROOT/"config"/"lean-promotion-readiness.json").read_text(encoding="utf-8"))

def validate():
    r=load()
    if r.get("research_only") is not True: raise AssertionError("Phase 3E must remain research-only")
    for key in ("runtime_promotion_allowed","gitlink_change_allowed","fork_promotion_allowed","package_release_allowed","promotion_adr_approved"):
        if r.get(key) is not False: raise AssertionError(f"{key} unexpectedly enabled")
    if r.get("current_hard_stop") is not True: raise AssertionError("promotion hard stop must remain active")
    if r.get("windows_11_x64_physical_smoke")!="PENDING_DESKTOP_SESSION":
        raise AssertionError("Windows 11 physical smoke must remain pending in mobile-only phase")
    if r.get("goals",{}).get("stream_backed_bridge") is not True:
        raise AssertionError("stream-backed bridge goal missing")
    sbom_path=ROOT/"supply-chain"/"patched-lean-phase3e.cdx.json"
    license_path=ROOT/"supply-chain"/"patched-lean-phase3e-license-review.json"
    if not sbom_path.is_file() or not license_path.is_file():
        raise AssertionError("patched LEAN static supply-chain evidence missing")
    sbom=json.loads(sbom_path.read_text(encoding="utf-8"))
    review=json.loads(license_path.read_text(encoding="utf-8"))
    if sbom.get("bomFormat")!="CycloneDX" or sbom.get("specVersion")!="1.7":
        raise AssertionError("patched LEAN SBOM format drift")
    if len(sbom.get("components",[]))!=59:
        raise AssertionError("patched LEAN SBOM component count drift")
    if review.get("package_count")!=59 or review.get("unknown_license_count")!=0:
        raise AssertionError("patched LEAN license evidence incomplete")
    if review.get("release_clearance") is not False:
        raise AssertionError("license identification must not imply release clearance")
    if any((x.get("license",{}).get("source") or "").startswith(("/", "\\")) for x in review.get("packages",[])):
        raise AssertionError("patched LEAN license evidence contains absolute runner path")
    return r

def main():
    p=argparse.ArgumentParser();p.add_argument("--require-promotion",action="store_true");a=p.parse_args()
    r=validate();print("QROS Phase 3E promotion-readiness boundary: PASS")
    if a.require_promotion and not r["runtime_promotion_allowed"]:
        print("QROS Phase 3E runtime promotion: DENY",file=sys.stderr);return 2
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except AssertionError as e:
        print("QROS Phase 3E promotion-readiness boundary: FAIL:",e,file=sys.stderr);raise SystemExit(1)
