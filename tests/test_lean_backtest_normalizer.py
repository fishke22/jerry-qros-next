import unittest

from qros_lean.backtest import normalize_result


class LeanBacktestNormalizerTests(unittest.TestCase):
    def test_normalized_result_is_stable_and_review_only(self):
        raw = {
            "statistics": {
                "QROS Rows": "5",
                "QROS Sum": "510.0000",
                "QROS Last": "104.0000",
                "Total Orders": "0",
            }
        }
        kwargs = {
            "algorithm_hash": "sha256:" + "a" * 64,
            "input_hash": "sha256:" + "b" * 64,
            "config_hash": "sha256:" + "c" * 64,
        }
        first = normalize_result(raw, **kwargs)
        second = normalize_result(raw, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["normalized_hash"], second["normalized_hash"])
        self.assertTrue(first["research_only"])
        self.assertFalse(first["gate_opened"])
        self.assertEqual(first["classification"], "PASS_REVIEW_ONLY")

    def test_statistic_mismatch_fails_closed(self):
        raw = {
            "statistics": {
                "QROS Rows": "4",
                "QROS Sum": "510.0000",
                "QROS Last": "104.0000",
                "Total Orders": "0",
            }
        }
        with self.assertRaises(RuntimeError):
            normalize_result(
                raw,
                algorithm_hash="sha256:" + "a" * 64,
                input_hash="sha256:" + "b" * 64,
                config_hash="sha256:" + "c" * 64,
            )


if __name__ == "__main__":
    unittest.main()
