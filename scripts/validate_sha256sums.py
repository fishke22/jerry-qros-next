from __future__ import annotations
import hashlib
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"supply-chain"/"SHA256SUMS"
LINE=re.compile(r"^([0-9a-f]{64})  (.+)$")

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
            raise AssertionError(f"checksummed file missing: {rel}")
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=expected:
            raise AssertionError(f"SHA256 mismatch: {rel}")
        print("PASS sha256",rel)
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
    print("QROS SHA256 gate: PASS")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except AssertionError as exc:
        print("QROS SHA256 gate: FAIL:",exc,file=sys.stderr)
        raise SystemExit(1)
