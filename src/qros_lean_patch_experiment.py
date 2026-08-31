from __future__ import annotations

import importlib.util
from pathlib import Path

_script = Path(__file__).resolve().parents[2] / "scripts" / "apply_lean_patch_experiment.py"
_spec = importlib.util.spec_from_file_location("_qros_lean_patch_experiment_script", _script)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)

CANDIDATES = _mod.CANDIDATES
apply = _mod.apply
