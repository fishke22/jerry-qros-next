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
