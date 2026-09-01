from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

LEAN_REVISION = "b692bf4788e8b54fc23bdcb5659666bf055ce89f"
PATCH_MODE = "DETERMINISTIC_CHECKOUT_TIME_NO_FORK_NO_GITLINK_CHANGE"
PATCH_SCRIPT_RELATIVE = "scripts/apply_lean_security_patch.py"
PATCH_GRAPH_RELATIVE = "supply-chain/lean/launcher-patched-nuget-graph.json"
COMPRESSION_RELATIVE = "Compression/QuantConnect.Compression.csproj"
MESSAGING_RELATIVE = "Messaging/QuantConnect.Messaging.csproj"

COMPRESSION_OLD = '    <PackageReference Include="DotNetZip" Version="1.16.0" />'
COMPRESSION_NEW = '    <PackageReference Include="ProDotNetZip" Version="1.20.0" />'
MESSAGING_NETMQ_OLD = '    <PackageReference Include="NetMQ" Version="4.0.1.6" />\n'
MESSAGING_NETMQ_NEW = ''
MESSAGING_ITEM_OLD = (
    '  <ItemGroup>\n'
    '    <Compile Include="..\\\\Common\\\\Properties\\\\SharedAssemblyInfo.cs" '
    'Link="Properties\\\\SharedAssemblyInfo.cs" />\n'
    '  </ItemGroup>'
)
MESSAGING_ITEM_NEW = (
    '  <ItemGroup>\n'
    '    <Compile Remove="StreamingMessageHandler.cs" />\n'
    '    <Compile Include="..\\\\Common\\\\Properties\\\\SharedAssemblyInfo.cs" '
    'Link="Properties\\\\SharedAssemblyInfo.cs" />\n'
    '  </ItemGroup>'
)
EXPECTED_MODIFIED_PATHS = {COMPRESSION_RELATIVE, MESSAGING_RELATIVE}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: dict) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def replace_exact_text(text: str, old: str, new: str, label: str) -> str:
    require(old in text, f"expected patch anchor missing: {label}")
    require(text.count(old) == 1, f"patch anchor is not unique: {label}")
    return text.replace(old, new)


def expected_patched_texts(compression_text: str, messaging_text: str) -> tuple[str, str]:
    compression_text = replace_exact_text(
        compression_text, COMPRESSION_OLD, COMPRESSION_NEW, COMPRESSION_RELATIVE
    )
    messaging_text = replace_exact_text(
        messaging_text, MESSAGING_NETMQ_OLD, MESSAGING_NETMQ_NEW, MESSAGING_RELATIVE
    )
    messaging_text = replace_exact_text(
        messaging_text, MESSAGING_ITEM_OLD, MESSAGING_ITEM_NEW, MESSAGING_RELATIVE
    )
    return compression_text, messaging_text


def _git(lean: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(lean), *args], text=True
    ).strip()


def _base_text(lean: Path, relative: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(lean), "show", f"{LEAN_REVISION}:{relative}"],
        text=True,
    )


def expected_patched_files(root: Path) -> dict[str, str]:
    lean = root / "external" / "lean"
    compression, messaging = expected_patched_texts(
        _base_text(lean, COMPRESSION_RELATIVE),
        _base_text(lean, MESSAGING_RELATIVE),
    )
    return {
        COMPRESSION_RELATIVE: compression,
        MESSAGING_RELATIVE: messaging,
    }


def verify_clean_base(root: Path) -> None:
    lean = root / "external" / "lean"
    head = _git(lean, "rev-parse", "HEAD")
    require(head == LEAN_REVISION, f"LEAN revision drift: {head}")
    status = _git(lean, "status", "--porcelain=v1", "--untracked-files=all")
    require(status == "", "LEAN base checkout is not clean; refusing to patch")


def verify_patched_checkout(root: Path) -> None:
    lean = root / "external" / "lean"
    head = _git(lean, "rev-parse", "HEAD")
    require(head == LEAN_REVISION, f"LEAN revision drift: {head}")

    staged = _git(lean, "diff", "--cached", "--name-only")
    untracked = _git(lean, "ls-files", "--others", "--exclude-standard")
    changed = {
        line for line in _git(lean, "diff", "--name-only").splitlines() if line
    }
    require(staged == "", "LEAN checkout contains staged changes")
    require(untracked == "", "LEAN checkout contains unexpected untracked files")
    require(
        changed == EXPECTED_MODIFIED_PATHS,
        f"LEAN patched file set drift: {sorted(changed)}",
    )

    expected = expected_patched_files(root)
    for relative, expected_text in expected.items():
        actual = (lean / relative).read_text(encoding="utf-8")
        require(actual == expected_text, f"LEAN post-patch content drift: {relative}")

    subprocess.run(
        ["git", "-C", str(lean), "diff", "--check"],
        check=True,
        text=True,
        capture_output=True,
    )


def apply_patch(root: Path) -> None:
    verify_clean_base(root)
    lean = root / "external" / "lean"
    expected = expected_patched_files(root)
    for relative, content in expected.items():
        (lean / relative).write_text(content, encoding="utf-8")
    verify_patched_checkout(root)


def runtime_overlay_fingerprint(root: Path, launcher: Path) -> dict[str, str]:
    verify_patched_checkout(root)
    require(launcher.is_file(), "LEAN Launcher is not built")
    return {
        "mode": PATCH_MODE,
        "patch_script_hash": sha256_file(root / PATCH_SCRIPT_RELATIVE),
        "patched_graph_hash": sha256_file(root / PATCH_GRAPH_RELATIVE),
        "launcher_assembly_hash": sha256_file(launcher),
    }


def overlay_identity(runtime_overlay: dict[str, str]) -> str:
    required = {
        "mode",
        "patch_script_hash",
        "patched_graph_hash",
        "launcher_assembly_hash",
    }
    require(set(runtime_overlay) == required, "runtime overlay fingerprint fields drift")
    require(runtime_overlay["mode"] == PATCH_MODE, "runtime overlay mode drift")
    for key in required - {"mode"}:
        value = runtime_overlay[key]
        require(
            isinstance(value, str)
            and value.startswith("sha256:")
            and len(value) == 71,
            f"invalid runtime overlay hash: {key}",
        )
    material = {"engine_revision": LEAN_REVISION, "runtime_overlay": runtime_overlay}
    return "sha256:" + hashlib.sha256(canonical_bytes(material)).hexdigest()
