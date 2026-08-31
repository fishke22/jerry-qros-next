from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ENGINE = "b692bf4788e8b54fc23bdcb5659666bf055ce89f"
EXPECTED_BLOCKERS = {
    ("DotNetZip", "1.16.0", "GHSA-xhg6-9j5j-w4vf", "HIGH"),
    ("System.Drawing.Common", "4.7.0", "GHSA-rxg9-xrhp-64gj", "CRITICAL"),
    ("System.Net.Http.WinHttpHandler", "4.4.0", "GHSA-6xh7-4v2w-36q6", "HIGH"),
    ("System.Private.ServiceModel", "4.4.0", "GHSA-jc8g-xhw5-6x46", "HIGH"),
    ("System.ServiceModel.Primitives", "4.4.0", "GHSA-jc8g-xhw5-6x46", "HIGH"),
}


def load_review() -> dict:
    return json.loads(
        (ROOT / "config" / "lean-security-review.json").read_text(encoding="utf-8")
    )


def validate_review() -> dict:
    review = load_review()
    if review.get("engine_revision") != EXPECTED_ENGINE:
        raise AssertionError("LEAN security review revision drift")
    if review.get("unknown_is_deny") is not True:
        raise AssertionError("LEAN security review must remain fail-closed")
    if review.get("runtime_promotion_allowed") is not False:
        raise AssertionError("LEAN runtime promotion unexpectedly allowed")
    if review.get("phase3b_merge_allowed") is not False:
        raise AssertionError("Phase 3B merge unexpectedly allowed")
    observed = {
        (x["package"], x["version"], x["advisory"], x["severity"])
        for x in review.get("blockers", [])
    }
    if not EXPECTED_BLOCKERS.issubset(observed):
        raise AssertionError("known LEAN security blocker missing from review")
    if review.get("remediation_gate", {}).get("currently_satisfied") is not False:
        raise AssertionError("LEAN remediation gate unexpectedly satisfied")
    return review


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--enforce-runtime-promotion", action="store_true")
    args = parser.parse_args()
    review = validate_review()
    print("QROS LEAN security review representation: PASS")
    if args.enforce_runtime_promotion and not review["runtime_promotion_allowed"]:
        print(
            "QROS LEAN runtime promotion gate: BLOCKED by known HIGH/CRITICAL dependencies",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print("QROS LEAN security review: FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)
