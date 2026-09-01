from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"external"/"lean"/"Compression"/"QrosRuntimeCompressionCompat.cs"
if not p.is_file():
    print("QROS streaming bridge source gate: FAIL: bridge missing",file=sys.stderr);raise SystemExit(1)
text=p.read_text(encoding="utf-8")
required=["private readonly ZipArchiveEntry _sourceEntry;","return _sourceEntry.Open();","entry.CopyTo(target);","LoadSourceArchive()"]
for item in required:
    if item not in text:
        print("QROS streaming bridge source gate: FAIL:",item,file=sys.stderr);raise SystemExit(1)
for forbidden in ["source.CopyTo(memory);","memory.ToArray()","_entries.Add(new ZipEntry(entry.FullName, memory.ToArray()))"]:
    if forbidden in text:
        print("QROS streaming bridge source gate: FAIL: full-entry buffering remains",file=sys.stderr);raise SystemExit(1)
print("QROS streaming bridge source gate: PASS")
