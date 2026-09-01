from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load() -> tuple[dict, dict]:
    research = json.loads((ROOT / "config" / "lean-remediation-research.json").read_text(encoding="utf-8"))
    experiment = json.loads((ROOT / "config" / "lean-patch-experiment.json").read_text(encoding="utf-8"))
    return research, experiment


def validate() -> tuple[dict, dict]:
    research, experiment = load()
    if research.get("architecture_amendment_approved") is not True:
        raise AssertionError("Option B research amendment not approved")
    if research.get("lean_source_patch_experiment_authorized") is not True:
        raise AssertionError("research patch experiment not authorized")
    for key in ("lean_source_patch_authorized","lean_fork_authorized","lean_gitlink_change_authorized","runtime_promotion_allowed"):
        if research.get(key) is not False:
            raise AssertionError(f"{key} unexpectedly enabled")
    if experiment.get("research_only") is not True:
        raise AssertionError("experiment must be research-only")
    for key in ("runtime_promotion_allowed","gitlink_change_allowed","fork_promotion_allowed","dependency_override_promotion_allowed"):
        if experiment.get(key) is not False:
            raise AssertionError(f"{key} unexpectedly enabled")
    candidate=experiment["candidates"]["MESSAGING_NETMQ_4_0_4_3"]
    if candidate["old_version"]!="4.0.1.6" or candidate["new_version"]!="4.0.4.3":
        raise AssertionError("NetMQ candidate drift")
    if candidate["promotion_allowed"] is not False:
        raise AssertionError("candidate promotion unexpectedly allowed")
    return research, experiment


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--require-runtime-promotion", action="store_true")
    args=parser.parse_args()
    validate()
    print("QROS Phase 3D experiment authorization gate: PASS")
    if args.require_runtime_promotion:
        print("QROS Phase 3D runtime promotion: DENY", file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print("QROS Phase 3D experiment authorization gate: FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)
