from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED="b692bf4788e8b54fc23bdcb5659666bf055ce89f"
def fail(m): raise AssertionError(m)
def gitlink():
    parts=subprocess.check_output(["git","ls-tree","HEAD","external/lean"],cwd=ROOT,text=True).strip().split()
    if len(parts)<3 or parts[0]!="160000" or parts[1]!="commit": fail("external/lean is not a gitlink")
    return parts[2]
def main():
    p=argparse.ArgumentParser();p.add_argument("--require-populated",action="store_true");a=p.parse_args()
    m=(ROOT/".gitmodules").read_text(encoding="utf-8")
    if "path = external/lean" not in m or "url = https://github.com/QuantConnect/Lean.git" not in m: fail(".gitmodules drift")
    if gitlink()!=EXPECTED: fail("LEAN gitlink mismatch")
    reg=json.loads((ROOT/"config/dependency-registry.json").read_text(encoding="utf-8"))
    d=next((x for x in reg["dependencies"] if x["dependency_id"]=="quantconnect-lean"),None)
    if not d or d.get("status")!="ADOPTED" or d.get("pin_type")!="GIT_SUBMODULE_SHA40" or d.get("revision")!=EXPECTED: fail("LEAN registry pin drift")
    if a.require_populated:
        lean=ROOT/"external"/"lean"
        actual=subprocess.check_output(["git","-C",str(lean),"rev-parse","HEAD"],text=True).strip()
        if actual!=EXPECTED: fail("populated LEAN revision mismatch")
        project=(lean/"Launcher"/"QuantConnect.Lean.Launcher.csproj").read_text(encoding="utf-8")
        if "<TargetFramework>net10.0</TargetFramework>" not in project: fail("LEAN Launcher framework drift")
    print("QROS Phase 3 LEAN pin gate: PASS");return 0
if __name__=="__main__":
    try:raise SystemExit(main())
    except (AssertionError,subprocess.CalledProcessError) as exc:
        print("QROS Phase 3 LEAN pin gate: FAIL:",exc,file=sys.stderr);raise SystemExit(1)
