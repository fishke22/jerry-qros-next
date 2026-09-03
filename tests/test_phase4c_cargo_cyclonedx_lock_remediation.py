import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class Phase4CCargoCycloneDxLockRemediationTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(
            (
                ROOT
                / "config"
                / "phase4c-cargo-cyclonedx-lock-remediation.json"
            ).read_text(encoding="utf-8")
        )
        self.workflow=(
            ROOT
            / ".github"
            / "workflows"
            / "phase4c-cargo-cyclonedx-lock-remediation.yml"
        ).read_text(encoding="utf-8")

    def test_exact_upstream_release_is_pinned(self):
        u=self.policy["upstream"]
        self.assertEqual(u["version"],"0.5.9")
        self.assertEqual(
            u["release_commit"],
            "e58bd5590212f82c5b7e16dd3e2e819b0dbea5b1",
        )
        self.assertFalse(u["native_1_7_support_released"])
        self.assertEqual(u["native_1_7_open_pr"],872)
        self.assertIn(u["release_commit"],self.workflow)

    def test_only_xml_rs_lock_entry_may_change(self):
        r=self.policy["lock_remediation"]
        self.assertEqual(r["package"],"xml-rs")
        self.assertEqual(r["from_version"],"0.8.19")
        self.assertEqual(r["to_version"],"0.8.27")
        self.assertTrue(r["from_yanked"])
        self.assertFalse(r["source_code_change_authorized"])
        self.assertTrue(r["only_lock_entry_change_authorized"])
        self.assertTrue(r["all_other_locked_packages_must_match"])
        self.assertEqual(
            r["patched_lock_path"],
            "supply-chain/tool-locks/cargo-cyclonedx-0.5.9-qros.lock",
        )
        self.assertEqual(
            r["patched_lock_sha256"],
            "f24c56121784fe36ee9f14868b7f6386f1dd3fe640a3d2ee3e5aed4fea986e7a",
        )
        self.assertIn("Committed lock changes packages other than xml-rs", self.workflow)
        self.assertNotIn("cargo update", self.workflow)

    def test_committed_lock_and_security_gate_are_required(self):
        self.assertIn(
            "supply-chain/tool-locks/cargo-cyclonedx-0.5.9-qros.lock",
            self.workflow,
        )
        self.assertIn(
            "cargo-audit --version 0.22.2",
            self.workflow,
        )
        self.assertIn(
            "QROS_PHASE4C_TOOL_RUSTSEC_GATE=PASS",
            self.workflow,
        )
        self.assertIn(
            "QROS_PHASE4C_TOOL_LICENSE_METADATA_GATE=PASS",
            self.workflow,
        )

    def test_patched_tool_must_use_locked_source_build(self):
        self.assertIn("cargo install",self.workflow)
        self.assertIn("--locked",self.workflow)
        self.assertIn(
            ".phase4c-remediation/upstream/cargo-cyclonedx",
            self.workflow,
        )
        self.assertNotIn("cargo install cargo-cyclonedx --version",self.workflow)

    def test_output_must_remain_byte_identical(self):
        f=self.policy["fidelity"]
        self.assertTrue(f["byte_identical_output_required"])
        self.assertEqual(
            f["expected_cyclonedx_1_5_sha256"],
            "50e315c02680106ff3004e6e194f58d4cbbd8732fab33aff08ff122972da3623",
        )
        self.assertIn(
            "QROS_PHASE4C_REMEDIATED_SBOM_BYTE_IDENTITY=PASS",
            self.workflow,
        )

    def test_license_is_conservative_and_distribution_closed(self):
        l=self.policy["license"]
        self.assertEqual(
            l["qros_conservative_effective_disposition"],
            "Apache-2.0 AND MIT",
        )
        self.assertTrue(l["mit_notice_preservation_required"])
        self.assertFalse(l["external_distribution_authorized"])

    def test_hard_gates_and_adoption_remain_closed(self):
        self.assertEqual(
            self.policy["status"],
            "PATCHED_LOCK_PRESERVED_SECURITY_REVIEW_PENDING",
        )
        s=self.policy["scope"]
        self.assertTrue(s["lock_remediation_research_authorized"])
        self.assertTrue(s["patched_tool_build_test_authorized"])
        self.assertFalse(s["permanent_tool_adoption_authorized"])
        self.assertFalse(s["dependency_registry_promotion_authorized"])
        self.assertFalse(s["canonical_sbom_1_7_promotion_authorized"])
        g=self.policy["hard_gates"]
        self.assertTrue(g["zero_cost_required"])
        self.assertFalse(g["package_authorized"])
        self.assertFalse(g["release_authorized"])
        self.assertFalse(g["yuanta_integration_authorized"])
        self.assertFalse(g["live_trading_authorized"])


if __name__=="__main__":
    unittest.main()
