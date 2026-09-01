from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"external"/"lean"/"Tests"/"QuantConnect.Tests.csproj"
old='<PackageReference Include="NetMQ" Version="4.0.1.6" />'
new='<PackageReference Include="NetMQ" Version="4.0.4.3" />'
text=path.read_text(encoding="utf-8-sig")
if text.count(old)!=1:
    raise SystemExit("expected exact Tests NetMQ line not found once")
path.write_text(text.replace(old,new),encoding="utf-8")
print("QROS Phase 3E test harness NetMQ adjustment: PASS")
