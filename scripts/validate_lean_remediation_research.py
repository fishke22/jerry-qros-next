from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED = "b692bf4788e8b54fc23bdcb5659666bf055ce89f"
LATEST_OBSERVED = "abeb0a0627ec484b92291c45c3f2553726c26199"


def load() -> dict:
    return json.loads(
        (ROOT / "config" / "lean-remediation-research.json").read_text(encoding="utf-8")
    )


def validate() -> dict:
    r = load()
    if r.get("research_only") is not True:
        raise AssertionError("Phase 3C must remain research-only")
    if r.get("architecture_amendment_approved") is not True:
        raise AssertionError("Option B research amendment must be approved")
    if r.get("lean_source_patch_experiment_authorized") is not True:
        raise AssertionError("Option B research patch experiment must be authorized")
    for key in (
        "lean_source_patch_authorized",
        "lean_fork_authorized",
        "lean_gitlink_change_authorized",
        "runtime_promotion_allowed",
    ):
        if r.get(key) is not False:
            raise AssertionError(f"{key} unexpectedly enabled")
    if r.get("pinned_lean_revision") != PINNED:
        raise AssertionError("pinned LEAN revision drift")
    u = r.get("upstream", {})
    if u.get("latest_master_revision") != LATEST_OBSERVED:
        raise AssertionError("upstream observation revision drift")
    if u.get("latest_master_dotnetzip_version") != "1.16.0":
        raise AssertionError("DotNetZip upstream observation drift")
    if u.get("official_revision_remediation_available") is not False:
        raise AssertionError("official remediation unexpectedly marked available")
    if u.get("issue_8795", {}).get("state") != "OPEN":
        raise AssertionError("issue #8795 state evidence drift")
    candidates = {x["candidate"]: x for x in r.get("candidate_paths", [])}
    for rejected in ("DROP_IN_DOTNETZIP_FORK", "SUPPRESS_NUGET_SECURITY_WARNINGS"):
        if candidates.get(rejected, {}).get("status") != "REJECTED":
            raise AssertionError(f"{rejected} must remain rejected")
    gate = r.get("next_gate", {})
    if gate.get("research_evidence_accepted") is not True:
        raise AssertionError("Phase 3C research evidence not accepted")
    if gate.get("security_remediation_available") is not True:
        raise AssertionError("Phase 3D research remediation candidate must be represented")
    if gate.get("security_remediation_scope") != "RESEARCH_PATCH_CANDIDATE_ONLY":
        raise AssertionError("security remediation scope must remain research-only")
    if gate.get("hard_stop_active") is not True:
        raise AssertionError("security hard stop must remain active")
    if gate.get("architecture_amendment_approved") is not True:
        raise AssertionError("Option B research amendment missing from next gate")
    return r


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-remediation", action="store_true")
    args = parser.parse_args()
    r = validate()
    print("QROS Phase 3C research-boundary validation: PASS")
    if args.require_remediation and not r["next_gate"].get("runtime_promotion_allowed", False):
        print("QROS Phase 3C runtime-promotion remediation gate: BLOCKED", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print("QROS Phase 3C research-boundary validation: FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)
