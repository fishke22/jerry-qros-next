import unittest

from qros_lean.backtest import (
    normalize_result,
    semantic_regression_hash,
    semantic_regression_projection,
)


class LeanBacktestNormalizerTests(unittest.TestCase):
    def _raw(self):
        return {
            "statistics": {
                "QROS Rows": "5",
                "QROS Sum": "510.0000",
                "QROS Last": "104.0000",
                "Total Orders": "0",
            }
        }

    def _kwargs(self, algorithm_char="a"):
        return {
            "algorithm_hash": "sha256:" + algorithm_char * 64,
            "input_hash": "sha256:" + "b" * 64,
            "config_hash": "sha256:" + "c" * 64,
        }

    def test_normalized_result_is_stable_and_review_only(self):
        first = normalize_result(self._raw(), **self._kwargs())
        second = normalize_result(self._raw(), **self._kwargs())
        self.assertEqual(first, second)
        self.assertEqual(first["normalized_hash"], second["normalized_hash"])
        self.assertTrue(first["research_only"])
        self.assertFalse(first["gate_opened"])
        self.assertEqual(first["classification"], "PASS_REVIEW_ONLY")

    def test_semantic_regression_identity_excludes_only_build_identity(self):
        first = normalize_result(self._raw(), **self._kwargs("a"))
        rebuilt = normalize_result(self._raw(), **self._kwargs("d"))

        self.assertNotEqual(first["normalized_hash"], rebuilt["normalized_hash"])
        self.assertEqual(
            semantic_regression_projection(first),
            semantic_regression_projection(rebuilt),
        )
        self.assertEqual(
            semantic_regression_hash(first), semantic_regression_hash(rebuilt)
        )
        self.assertNotIn(
            "algorithm_assembly_hash", semantic_regression_projection(first)
        )
        self.assertNotIn("normalized_hash", semantic_regression_projection(first))

    def test_semantic_regression_identity_covers_input_and_statistics(self):
        first = normalize_result(self._raw(), **self._kwargs())
        changed_input = dict(first)
        changed_input["input_hash"] = "sha256:" + "e" * 64
        changed_stats = dict(first)
        changed_stats["statistics"] = dict(first["statistics"])
        changed_stats["statistics"]["qros_sum"] = "511.0000"

        self.assertNotEqual(
            semantic_regression_hash(first), semantic_regression_hash(changed_input)
        )
        self.assertNotEqual(
            semantic_regression_hash(first), semantic_regression_hash(changed_stats)
        )

    def test_statistic_mismatch_fails_closed(self):
        raw = self._raw()
        raw["statistics"]["QROS Rows"] = "4"
        with self.assertRaises(RuntimeError):
            normalize_result(raw, **self._kwargs())


if __name__ == "__main__":
    unittest.main()
