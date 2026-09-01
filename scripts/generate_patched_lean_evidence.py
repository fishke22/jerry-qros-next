from __future__ import annotations
import argparse,json,os,xml.etree.ElementTree as ET
from pathlib import Path

def license_for(name,version):
    root=Path.home()/".nuget"/"packages"/name.lower()/version.lower()
    nuspecs=list(root.glob("*.nuspec"))
    if not nuspecs:
        return {"status":"UNKNOWN","value":None,"source":"NUSPEC_MISSING"}
    tree=ET.parse(nuspecs[0]); meta=tree.getroot()
    lic=None;url=None
    for el in meta.iter():
        tag=el.tag.split("}")[-1]
        if tag=="license" and el.text:
            lic={"type":el.attrib.get("type","unknown"),"value":el.text.strip()}
        elif tag=="licenseUrl" and el.text:
            url=el.text.strip()
    if lic:
        return {"status":"EXPRESSION" if lic["type"]=="expression" else "FILE_OR_OTHER","value":lic["value"],"source":str(nuspecs[0])}
    if url:
        return {"status":"URL_ONLY","value":url,"source":str(nuspecs[0])}
    return {"status":"UNKNOWN","value":None,"source":str(nuspecs[0])}

def main():
    p=argparse.ArgumentParser();p.add_argument("--assets",type=Path,required=True);p.add_argument("--sbom",type=Path,required=True);p.add_argument("--licenses",type=Path,required=True);a=p.parse_args()
    data=json.loads(a.assets.read_text(encoding="utf-8"))
    target_name=next((k for k in data["targets"] if k.startswith("net10.0")),None)
    if not target_name: raise RuntimeError("net10.0 target missing")
    target=data["targets"][target_name]
    libraries=data["libraries"]
    packages=[]
    resolved={}
    for key,item in target.items():
        lib=libraries.get(key,{})
        if lib.get("type")!="package": continue
        name,version=key.rsplit("/",1);resolved[name.lower()]=(name,version)
    for lname,(name,version) in sorted(resolved.items()):
        lic=license_for(name,version)
        packages.append({"name":name,"version":version,"license":lic})
    refs={name.lower():f"pkg:nuget/{name}@{version}" for name,version in resolved.values()}
    components=[]
    dependencies=[]
    for pkg in packages:
        ref=refs[pkg["name"].lower()]
        lic=pkg["license"]
        lics=[]
        if lic["status"]=="EXPRESSION": lics=[{"expression":lic["value"]}]
        elif lic["value"]: lics=[{"license":{"name":lic["status"],"url":lic["value"] if str(lic["value"]).startswith("http") else None}}]
        components.append({"type":"library","bom-ref":ref,"name":pkg["name"],"version":pkg["version"],"purl":ref,"licenses":lics,"properties":[{"name":"qros:license-status","value":lic["status"]}]})
        key=f'{pkg["name"]}/{pkg["version"]}'
        deps=[]
        for dname in target.get(key,{}).get("dependencies",{}):
            if dname.lower() in refs: deps.append(refs[dname.lower()])
        dependencies.append({"ref":ref,"dependsOn":sorted(set(deps))})
    rootref="pkg:generic/qros-patched-lean@phase3e"
    bom={"bomFormat":"CycloneDX","specVersion":"1.7","serialNumber":"urn:uuid:00000000-0000-0000-0000-00000000003e","version":1,
         "metadata":{"component":{"type":"application","bom-ref":rootref,"name":"QROS patched LEAN research candidate","version":"phase3e","properties":[{"name":"qros:research-only","value":"true"},{"name":"qros:base-lean-revision","value":"b692bf4788e8b54fc23bdcb5659666bf055ce89f"}]}},
         "components":components,"dependencies":[{"ref":rootref,"dependsOn":sorted(refs.values())}]+dependencies}
    unknown=[x for x in packages if x["license"]["status"]=="UNKNOWN"]
    review={"review_version":1,"scope":"PATCHED_LEAN_LAUNCHER_TRANSITIVE_NUGET_GRAPH","package_count":len(packages),"unknown_license_count":len(unknown),
            "status":"PASS" if not unknown else "BLOCKED_UNKNOWN_LICENSE","packages":packages}
    a.sbom.write_text(json.dumps(bom,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    a.licenses.write_text(json.dumps(review,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
    print("QROS_PATCHED_SBOM_JSON="+json.dumps(bom,sort_keys=True,separators=(",",":")))
    print("QROS_PATCHED_LICENSE_JSON="+json.dumps(review,sort_keys=True,separators=(",",":")))
    print(f"QROS patched graph evidence: packages={len(packages)} unknown_licenses={len(unknown)}")
    return 0

if __name__=="__main__": raise SystemExit(main())
