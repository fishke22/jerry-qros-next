from __future__ import annotations

import base64
import gzip
import json
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

SPEC_VERSION="1.7"

def _local(tag:str)->str:
    return tag.rsplit("}",1)[-1]

def _nuspec_evidence(packages_root:Path,name:str,version:str)->dict:
    folder=packages_root/name.lower()/version
    files=sorted(folder.glob("*.nuspec"))
    if not files:
        return {"status":"MISSING","value":None,"source":None}
    root=ET.parse(files[0]).getroot()
    license_value=None
    license_type=None
    license_url=None
    for node in root.iter():
        local=_local(node.tag)
        if local=="license":
            license_value=(node.text or "").strip() or None
            license_type=node.attrib.get("type")
        elif local=="licenseUrl":
            license_url=(node.text or "").strip() or None
    if license_value and license_type=="expression":
        return {"status":"EXPRESSION","value":license_value,"source":str(files[0])}
    if license_value and license_type=="file":
        return {"status":"FILE","value":license_value,"source":str(files[0])}
    if license_url:
        return {"status":"URL_ONLY","value":license_url,"source":str(files[0])}
    return {"status":"MISSING","value":None,"source":str(files[0])}

def generate(assets_path:Path,packages_root:Path)->tuple[dict,dict]:
    assets=json.loads(assets_path.read_text(encoding="utf-8"))
    target_name=next((x for x in assets["targets"] if x.startswith("net10.0")),None)
    if not target_name:
        raise RuntimeError("net10.0 target missing from project.assets.json")
    target=assets["targets"][target_name]
    library_meta=assets.get("libraries",{})
    package_keys=sorted(k for k,v in library_meta.items() if v.get("type")=="package")
    by_name={k.split("/",1)[0].lower():k for k in package_keys}

    components=[]
    licenses=[]
    refs={}
    for key in package_keys:
        name,version=key.split("/",1)
        purl=f"pkg:nuget/{urllib.parse.quote(name,safe='._-')}@{urllib.parse.quote(version,safe='._-')}"
        refs[key]=purl
        evidence=_nuspec_evidence(packages_root,name,version)
        comp={"type":"library","bom-ref":purl,"name":name,"version":version,"purl":purl,
              "properties":[{"name":"qros:license-evidence-status","value":evidence["status"]}]}
        sha512=library_meta.get(key,{}).get("sha512")
        if sha512:
            try:
                comp["hashes"]=[{"alg":"SHA-512","content":base64.b64decode(sha512).hex()}]
            except Exception:
                comp["properties"].append({"name":"qros:nuget-sha512-raw","value":sha512})
        if evidence["status"]=="EXPRESSION":
            comp["licenses"]=[{"expression":evidence["value"]}]
        elif evidence["value"]:
            comp["properties"].append({"name":"qros:license-evidence-value","value":evidence["value"]})
        components.append(comp)
        licenses.append({"package":name,"version":version,**evidence})

    deps=[]
    for key in package_keys:
        depends=[]
        for dep_name in target.get(key,{}).get("dependencies",{}):
            dep_key=by_name.get(dep_name.lower())
            if dep_key:
                depends.append(refs[dep_key])
        deps.append({"ref":refs[key],"dependsOn":sorted(set(depends))})
    framework=assets.get("project",{}).get("frameworks",{}).get("net10.0",{})
    direct=[]
    for dep_name in framework.get("dependencies",{}):
        dep_key=by_name.get(dep_name.lower())
        if dep_key:
            direct.append(refs[dep_key])

    root_ref="pkg:generic/qros-patched-lean-candidate@phase3e"
    sbom={
        "bomFormat":"CycloneDX","specVersion":SPEC_VERSION,"serialNumber":"urn:uuid:00000000-0000-4000-8000-00000000003e","version":1,
        "metadata":{"component":{"type":"application","bom-ref":root_ref,"name":"QROS patched LEAN candidate","version":"phase3e",
          "properties":[
            {"name":"qros:research-only","value":"true"},
            {"name":"qros:runtime-promotion-allowed","value":"false"},
            {"name":"qros:base-lean-revision","value":"b692bf4788e8b54fc23bdcb5659666bf055ce89f"}]}},
        "components":components,
        "dependencies":[{"ref":root_ref,"dependsOn":sorted(set(direct))}]+deps
    }
    counts={}
    for x in licenses: counts[x["status"]]=counts.get(x["status"],0)+1
    report={"report_version":1,"target":target_name,"package_count":len(package_keys),"license_status_counts":counts,
            "promotion_ready":all(x["status"]=="EXPRESSION" for x in licenses),"packages":licenses}
    return sbom,report

def write_outputs(sbom:dict,report:dict,output:Path,license_output:Path)->None:
    output.write_text(json.dumps(sbom,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    license_output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def emit_gzip_base64(label:str,path:Path)->None:
    payload=gzip.compress(path.read_bytes(),compresslevel=9,mtime=0)
    print(f"{label}="+base64.b64encode(payload).decode("ascii"))
