from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIGESTS=ROOT/"packages"/"contracts"/"contract-digests.json"

def main()->int:
    data=json.loads(DIGESTS.read_text(encoding="utf-8"))
    if data.get("digest_type")!="git-blob-sha1":
        raise AssertionError("unsupported contract digest type")
    for item in data.get("contracts",[]):
        path=ROOT/item["path"]
        if not path.exists():
            raise AssertionError(f"missing immutable contract: {item['path']}")
        actual=subprocess.check_output(["git","hash-object",str(path)],cwd=ROOT,text=True).strip()
        if actual!=item["git_blob_sha"]:
            raise AssertionError(f"immutable contract changed in place: {item['path']}; create a new contract version")
        print("PASS immutable",item["path"])
    print("QROS contract immutability gate: PASS")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except (AssertionError,subprocess.CalledProcessError) as exc:
        print("QROS contract immutability gate: FAIL:",exc,file=sys.stderr)
        raise SystemExit(1)
