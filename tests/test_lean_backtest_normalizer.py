import unittest

from qros_lean.backtest import (
    normalize_result,
    semantic_regression_hash,
    semantic_regression_projection,
)
from qros_lean.runtime_overlay import PATCH_MODE


class LeanBacktestNormalizerTests(unittest.TestCase):
    def _raw(self):
        return {"statistics": {
            "QROS Rows": "5",
            "QROS Sum": "510.0000",
            "QROS Last": "104.0000",
            "Total Orders": "0",
        }}

    def _overlay(self, launcher_char="d", patch_char="e", graph_char="f"):
        return {
            "mode": PATCH_MODE,
            "patch_script_hash": "sha256:" + patch_char * 64,
            "patched_graph_hash": "sha256:" + graph_char * 64,
            "launcher_assembly_hash": "sha256:" + launcher_char * 64,
        }

    def _kwargs(self, algorithm_char="a", overlay=None):
        return {
            "algorithm_hash": "sha256:" + algorithm_char * 64,
            "input_hash": "sha256:" + "b" * 64,
            "config_hash": "sha256:" + "c" * 64,
            "runtime_overlay": overlay or self._overlay(),
        }

    def test_normalized_result_is_stable_runtime_bound_and_review_only(self):
        first = normalize_result(self._raw(), **self._kwargs())
        second = normalize_result(self._raw(), **self._kwargs())
        self.assertEqual(first, second)
        self.assertEqual(first["contract_version"], "2")
        self.assertEqual(first["normalized_hash"], second["normalized_hash"])
        self.assertTrue(first["research_only"])
        self.assertFalse(first["gate_opened"])
        self.assertEqual(first["classification"], "PASS_REVIEW_ONLY")
        self.assertTrue(first["overlay_identity"].startswith("sha256:"))

    def test_full_identity_changes_when_algorithm_or_overlay_changes(self):
        first = normalize_result(self._raw(), **self._kwargs("a"))
        rebuilt = normalize_result(self._raw(), **self._kwargs("d"))
        changed_overlay = normalize_result(
            self._raw(), **self._kwargs("a", self._overlay(launcher_char="9"))
        )
        self.assertNotEqual(first["normalized_hash"], rebuilt["normalized_hash"])
        self.assertNotEqual(first["normalized_hash"], changed_overlay["normalized_hash"])
        self.assertNotEqual(first["overlay_identity"], changed_overlay["overlay_identity"])

    def test_semantic_regression_excludes_build_and_overlay_identity(self):
        first = normalize_result(self._raw(), **self._kwargs("a"))
        rebuilt = normalize_result(
            self._raw(), **self._kwargs("d", self._overlay(launcher_char="9"))
        )
        self.assertEqual(semantic_regression_projection(first), semantic_regression_projection(rebuilt))
        self.assertEqual(semantic_regression_hash(first), semantic_regression_hash(rebuilt))
        projection = semantic_regression_projection(first)
        self.assertEqual(projection["contract_version"], "1")
        for field in ("algorithm_assembly_hash", "runtime_overlay", "overlay_identity", "normalized_hash"):
            self.assertNotIn(field, projection)

    def test_semantic_regression_identity_covers_input_and_statistics(self):
        first = normalize_result(self._raw(), **self._kwargs())
        changed_input = dict(first)
        changed_input["input_hash"] = "sha256:" + "e" * 64
        changed_stats = dict(first)
        changed_stats["statistics"] = dict(first["statistics"])
        changed_stats["statistics"]["qros_sum"] = "511.0000"
        self.assertNotEqual(semantic_regression_hash(first), semantic_regression_hash(changed_input))
        self.assertNotEqual(semantic_regression_hash(first), semantic_regression_hash(changed_stats))

    def test_statistic_mismatch_fails_closed(self):
        raw = self._raw()
        raw["statistics"]["QROS Rows"] = "4"
        with self.assertRaises(RuntimeError):
            normalize_result(raw, **self._kwargs())


if __name__ == "__main__":
    unittest.main()
