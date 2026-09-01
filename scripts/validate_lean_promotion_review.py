from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load():
    return json.loads((ROOT/"config"/"lean-promotion-review.json").read_text(encoding="utf-8"))

def validate():
    r=load()
    if r.get("review_only") is not True:
        raise AssertionError("Phase 3E must remain review-only")
    for key in ("runtime_promotion_allowed","main_merge_allowed","canonical_gitlink_change_allowed","package_release_allowed","yuanta_allowed","live_trading_allowed"):
        if r.get(key) is not False:
            raise AssertionError(f"{key} unexpectedly enabled")
    if r.get("promotion_decision") not in ("DENY_PENDING_REVIEW","DENY_REVIEW_COMPLETE"):
        raise AssertionError("promotion decision must remain deny")
    c=r.get("candidate",{})
    if c.get("messaging_netmq")!="4.0.4.3":
        raise AssertionError("NetMQ candidate drift")
    if c.get("netmq_official_tag_revision")!="ca87d32d5ca5d8a2675fb7a9925e4b3dc8c35010":
        raise AssertionError("NetMQ tag evidence drift")
    if r.get("next_gate",{}).get("independent_architecture_promotion_authorization_required") is not True:
        raise AssertionError("independent promotion authorization requirement missing")
    return r

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--require-promotion",action="store_true")
    args=p.parse_args()
    r=validate()
    print("QROS Phase 3E promotion-review boundary: PASS")
    if args.require_promotion and not r["runtime_promotion_allowed"]:
        print("QROS Phase 3E runtime promotion: DENY",file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except AssertionError as exc:
        print("QROS Phase 3E review validation: FAIL:",exc,file=sys.stderr)
        raise SystemExit(1)
