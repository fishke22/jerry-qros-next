from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from qros_patched_lean_sbom import emit_gzip_base64,generate,write_outputs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--assets",type=Path,required=True)
    p.add_argument("--packages-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--license-output",type=Path,required=True)
    p.add_argument("--emit-gzip-base64",action="store_true")
    a=p.parse_args()
    sbom,report=generate(a.assets,a.packages_root)
    write_outputs(sbom,report,a.output,a.license_output)
    print("QROS patched LEAN CycloneDX components:",len(sbom["components"]))
    print("QROS patched LEAN license status counts:",report["license_status_counts"])
    print("QROS patched LEAN automated license promotion ready:",report["promotion_ready"])
    if a.emit_gzip_base64:
        emit_gzip_base64("QROS_PATCHED_LEAN_SBOM_GZIP_BASE64",a.output)
        emit_gzip_base64("QROS_PATCHED_LEAN_LICENSE_GZIP_BASE64",a.license_output)
    return 0

if __name__=="__main__": raise SystemExit(main())
