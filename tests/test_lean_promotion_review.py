import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class LeanPromotionReviewTests(unittest.TestCase):
    def setUp(self):
        self.review=json.loads((ROOT/"config"/"lean-promotion-review.json").read_text(encoding="utf-8"))

    def test_review_cannot_promote_candidate(self):
        self.assertTrue(self.review["review_only"])
        self.assertFalse(self.review["runtime_promotion_allowed"])
        self.assertFalse(self.review["main_merge_allowed"])
        self.assertFalse(self.review["canonical_gitlink_change_allowed"])
        self.assertEqual(self.review["promotion_decision"],"DENY_PENDING_REVIEW")

    def test_all_evidence_starts_fail_closed(self):
        criteria=self.review["review_criteria"]
        for item in criteria.values():
            self.assertIn(item["status"],("PENDING_CI","UNVERIFIED"))
        self.assertFalse(self.review["next_gate"]["accepted"])
        self.assertTrue(self.review["next_gate"]["independent_architecture_promotion_authorization_required"])

if __name__=="__main__":
    unittest.main()
