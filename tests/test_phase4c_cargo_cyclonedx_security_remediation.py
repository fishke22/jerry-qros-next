import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class Phase4CCargoCycloneDxSecurityRemediationTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(
            (ROOT/"config"/"phase4c-cargo-cyclonedx-security-remediation.json")
            .read_text(encoding="utf-8")
        )
        self.workflow=(
            ROOT/".github"/"workflows"/"phase4c-cargo-cyclonedx-security-remediation.yml"
        ).read_text(encoding="utf-8")

    def test_vulnerability_and_unsound_findings_must_be_remediated(self):
        blockers={x["advisory"]:x for x in self.policy["rustsec_blockers"]}
        self.assertEqual(blockers["RUSTSEC-2026-0009"]["required_version"],">=0.3.47")
        self.assertEqual(blockers["RUSTSEC-2026-0190"]["required_version"],">=1.0.103")
        self.assertEqual(blockers["RUSTSEC-2026-0097"]["required_version"],"0.8.6")
        self.assertTrue(all(x["disposition"]=="MUST_REMEDIATE" for x in blockers.values()))

    def test_lock_only_updates_are_exact(self):
        u=self.policy["lock_updates"]
        self.assertEqual(u["anyhow"],"1.0.103")
        self.assertEqual(u["rand"],"0.8.6")
        self.assertEqual(u["time"],"0.3.47")
        self.assertFalse(u["source_changes_authorized"])
        self.assertFalse(u["manifest_changes_authorized"])
        self.assertIn("-p anyhow --precise 1.0.103",self.workflow)
        self.assertIn("-p rand --precise 0.8.6",self.workflow)
        self.assertIn("-p time --precise 0.3.47",self.workflow)

    def test_security_graph_excludes_only_dev_edges(self):
        s=self.policy["security_gate"]
        self.assertTrue(s["dev_edges_excluded"])
        self.assertFalse(s["reachable_vulnerabilities_allowed"])
        self.assertFalse(s["reachable_unsound_warnings_allowed"])
        self.assertFalse(s["reachable_unmaintained_warnings_allowed"])
        self.assertIn('k.get("kind")!="dev"',self.workflow)
        self.assertIn("Expected dev-only warning remains normal/build reachable",self.workflow)

    def test_security_and_license_gates_are_fail_closed(self):
        self.assertIn("QROS_PHASE4C_SECURITY_RUSTSEC_REACHABLE_GATE=PASS",self.workflow)
        self.assertIn("QROS_PHASE4C_SECURITY_LICENSE_GATE=PASS",self.workflow)
        self.assertIn("Denied malicious/compromised crate(s)",self.workflow)
        self.assertIn("Reachable license metadata missing",self.workflow)

    def test_qut_output_must_remain_identical(self):
        self.assertEqual(
            self.policy["fidelity"]["expected_cyclonedx_1_5_sha256"],
            "50e315c02680106ff3004e6e194f58d4cbbd8732fab33aff08ff122972da3623",
        )
        self.assertIn("QROS_PHASE4C_SECURITY_REMEDIATED_SBOM_BYTE_IDENTITY=PASS",self.workflow)

    def test_adoption_and_hard_gates_remain_closed(self):
        s=self.policy["scope"]
        self.assertFalse(s["remediated_lock_adoption_authorized"])
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
