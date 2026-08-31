from __future__ import annotations
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"supply-chain"/"SHA256SUMS"
LINE=re.compile(r"^([0-9a-f]{64})  (.+)$")

def canonical_git_bytes(rel: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", f"HEAD:{rel}"],
            cwd=ROOT,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        detail=exc.stderr.decode("utf-8", errors="replace").strip()
        raise AssertionError(f"cannot read canonical Git blob for {rel}: {detail}") from exc

def main()->int:
    lines=[x for x in MANIFEST.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not lines:
        raise AssertionError("SHA256SUMS must not be empty")
    seen=set()
    for line in lines:
        m=LINE.fullmatch(line)
        if not m:
            raise AssertionError(f"invalid SHA256SUMS line: {line!r}")
        expected,rel=m.groups()
        if rel in seen:
            raise AssertionError(f"duplicate checksum path: {rel}")
        seen.add(rel)
        path=ROOT/rel
        if not path.is_file():
            raise AssertionError(f"checksummed working-tree path missing: {rel}")
        actual=hashlib.sha256(canonical_git_bytes(rel)).hexdigest()
        if actual!=expected:
            raise AssertionError(f"canonical Git blob SHA256 mismatch: {rel}")
        print("PASS sha256-git-blob",rel)
    required={
        "config/cost-policy.json",
        "config/dependency-registry.json",
        "config/supply-chain-policy.json",
        "packages/contracts/contract-manifest.json",
        "packages/contracts/contract-digests.json",
        "supply-chain/bom.cdx.json",
        "supply-chain/dependency-license-manifest.json",
        "supply-chain/source-revisions.json",
        "supply-chain/build-environment.json",
        "supply-chain/provenance-manifest.json",
    }
    missing=required-seen
    if missing:
        raise AssertionError("critical evidence missing from SHA256SUMS: "+", ".join(sorted(missing)))
    print("QROS SHA256 canonical Git-blob gate: PASS")
    return 0

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print("QROS SHA256 gate: FAIL:",exc,file=sys.stderr)
        raise SystemExit(1)
