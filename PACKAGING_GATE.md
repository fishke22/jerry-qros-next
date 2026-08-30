# Packaging Gate

```text
PACKAGE_AUTHORIZED = false
RELEASE_AUTHORIZED = false
```

Forbidden until explicit authorization: MSI, MSIX, NSIS, production setup EXE/distributable package, GitHub Release, auto-updater, release signing, production Tauri bundling.

Allowed: source build, compile validation, tests, benchmark, and temporary development/test executables strictly required for validation.

Packaging and Yuanta authorization are independent gates.
