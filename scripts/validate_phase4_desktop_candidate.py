from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "desktop"
DESIGN = ROOT / "config" / "phase4-desktop-shell-design.json"

FORBIDDEN_NPM_PREFIXES = (
    "react-server-dom-",
    "@tauri-apps/plugin-shell",
    "@tauri-apps/plugin-fs",
    "@tauri-apps/plugin-http",
    "@tauri-apps/plugin-updater",
    "@tauri-apps/plugin-opener",
    "@tauri-apps/plugin-process",
)
FORBIDDEN_RUST = {
    ("arrayref", "0.3.10"),
    ("append-only-vec", "0.1.9"),
    ("internment", "0.8.7"),
}
FORBIDDEN_RUST_ALL = {
    "proc-macro1",
    "proc-macro-en",
    "aovine",
    "arone",
    "aronenao",
    "tinymember",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_npm_version(value: str) -> bool:
    return bool(re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", value))


def validate_static() -> None:
    design = load_json(DESIGN)
    auth = design["authorization"]
    require(auth["implementation_candidate_authorized"] is True, "candidate not authorized")
    require(auth["dependency_adoption_authorized"] is False, "dependency adoption unexpectedly allowed")
    require(auth["main_runtime_promotion_authorized"] is False, "main promotion unexpectedly allowed")
    for key in ("package_authorized", "release_authorized", "yuanta_integration_authorized", "live_trading_authorized"):
        require(auth[key] is False, f"hard gate opened: {key}")

    package = load_json(APP / "package.json")
    require(package["private"] is True, "desktop candidate must be private/non-publishable")
    require(package["version"] == "0.0.0", "candidate version drift")
    require(package["engines"] == {"node": "24.20.0", "npm": "11.19.0"}, "Node/npm engine drift")
    require(package["packageManager"] == "npm@11.19.0", "npm package manager drift")

    expected_runtime = {"react": "19.2.8", "react-dom": "19.2.8"}
    expected_dev = {
        "@tauri-apps/cli": "2.11.4",
        "@types/react": "19.2.18",
        "@types/react-dom": "19.2.5",
        "@vitejs/plugin-react": "6.1.1",
        "typescript": "7.0.2",
        "vite": "8.2.2",
    }
    require(package.get("dependencies") == expected_runtime, "runtime npm dependency set drift")
    require(package.get("devDependencies") == expected_dev, "dev npm dependency set drift")
    for section in ("dependencies", "devDependencies"):
        for name, version in package[section].items():
            require(exact_npm_version(version), f"floating/non-exact npm version: {name}={version}")
            require(not any(name == prefix or name.startswith(prefix) for prefix in FORBIDDEN_NPM_PREFIXES), f"forbidden npm package: {name}")

    scripts = package["scripts"]
    require(scripts["dev"] == "vite --host 127.0.0.1 --strictPort --port 1420", "Vite loopback policy drift")
    require(scripts["build"] == "tsc -b && vite build", "web build script drift")

    cargo = tomllib.loads((APP / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8"))
    require(cargo["package"]["publish"] is False, "Rust candidate must not be publishable")
    require(cargo["package"]["edition"] == "2024", "Rust edition drift")
    require(cargo["package"]["rust-version"] == "1.98.0", "Rust version drift")
    require(cargo["dependencies"] == {"tauri": {"version": "=2.11.5", "features": []}}, "Cargo runtime dependency drift")
    require(cargo["build-dependencies"] == {"tauri-build": {"version": "=2.6.3", "features": []}}, "Cargo build dependency drift")

    toolchain = tomllib.loads((APP / "rust-toolchain.toml").read_text(encoding="utf-8"))
    require(toolchain["toolchain"]["channel"] == "1.98.0", "Rust toolchain drift")
    require(toolchain["toolchain"]["profile"] == "minimal", "Rust profile drift")
    require(toolchain["toolchain"]["targets"] == ["x86_64-pc-windows-msvc"], "Rust target drift")

    vite = (APP / "vite.config.ts").read_text(encoding="utf-8")
    require('host: "127.0.0.1"' in vite, "Vite host is not loopback")
    require("strictPort: true" in vite, "Vite strictPort missing")
    require("0.0.0.0" not in vite and "--host" not in vite, "network-exposed Vite config")

    tauri = load_json(APP / "src-tauri" / "tauri.conf.json")
    require(tauri["build"]["devUrl"] == "http://127.0.0.1:1420", "Tauri devUrl drift")
    require(tauri["bundle"]["active"] is False, "Tauri bundling must remain disabled")
    security = tauri["app"]["security"]
    csp = security.get("csp")
    require(isinstance(csp, str) and "default-src 'self'" in csp, "restrictive CSP missing")
    require("https:" not in csp and "wss:" not in csp, "remote CSP endpoint allowed")

    source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in APP.rglob("*")
        if p.is_file() and p.suffix.lower() in {".ts", ".tsx", ".json", ".toml", ".rs"}
    )
    for token in ("plugin-shell", "plugin-fs", "plugin-http", "plugin-updater", "plugin-opener", "plugin-process"):
        require(token not in source, f"forbidden Tauri plugin token: {token}")


def validate_package_lock() -> None:
    lock = load_json(APP / "package-lock.json")
    require(lock.get("lockfileVersion") == 3, "unexpected npm lockfileVersion")
    root = lock["packages"][""]
    package = load_json(APP / "package.json")
    require(root.get("dependencies") == package["dependencies"], "package-lock root runtime deps drift")
    require(root.get("devDependencies") == package["devDependencies"], "package-lock root dev deps drift")

    for key, item in lock["packages"].items():
        if not key.startswith("node_modules/"):
            continue
        name = key.removeprefix("node_modules/")
        if name.startswith("@") and "/node_modules/" in name:
            name = name.split("/node_modules/")[-1]
        require(not any(name == prefix or name.startswith(prefix) for prefix in FORBIDDEN_NPM_PREFIXES), f"forbidden npm package resolved: {name}")
        if "resolved" in item:
            require(str(item["resolved"]).startswith("https://registry.npmjs.org/"), f"non-npm registry resolution: {name}")
            require(bool(item.get("integrity")), f"missing npm integrity: {name}")


def validate_cargo_lock() -> None:
    lock = tomllib.loads((APP / "src-tauri" / "Cargo.lock").read_text(encoding="utf-8"))
    require(lock.get("version") == 4, "unexpected Cargo.lock version")
    seen = {(p["name"], p["version"]) for p in lock["package"]}
    require(("tauri", "2.11.5") in seen, "tauri 2.11.5 not resolved")
    require(("tauri-build", "2.6.3") in seen, "tauri-build 2.6.3 not resolved")
    for name, version in seen:
        require((name, version) not in FORBIDDEN_RUST, f"known malicious Rust crate resolved: {name} {version}")
        require(name not in FORBIDDEN_RUST_ALL, f"known malicious Rust crate resolved: {name}")
    for item in lock["package"]:
        if str(item.get("source", "")).startswith("registry+"):
            require(bool(item.get("checksum")), f"missing Cargo registry checksum: {item['name']} {item['version']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-missing-locks", action="store_true")
    args = parser.parse_args()
    try:
        validate_static()
        package_lock = APP / "package-lock.json"
        cargo_lock = APP / "src-tauri" / "Cargo.lock"
        if not package_lock.exists() or not cargo_lock.exists():
            require(args.allow_missing_locks, "required lockfile missing")
        if package_lock.exists():
            validate_package_lock()
        if cargo_lock.exists():
            validate_cargo_lock()
    except (KeyError, json.JSONDecodeError, tomllib.TOMLDecodeError, RuntimeError) as exc:
        print(f"DENY: Phase 4 desktop candidate validation failed: {exc}")
        return 2
    print("Phase 4 desktop candidate gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
