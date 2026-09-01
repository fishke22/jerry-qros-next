import unittest

from scripts.validate_lean_patch_audit import validate_audit_documents


def doc(packages=None, *, framework="net10.0", problems=None, include_framework=True):
    project = {"path": "external/lean/Launcher/QuantConnect.Lean.Launcher.csproj"}
    if include_framework:
        project["frameworks"] = [{
            "framework": framework,
            "topLevelPackages": packages or [],
            "transitivePackages": [],
        }]
    result = {"version": 1, "projects": [project]}
    if problems is not None:
        result["problems"] = problems
    return result


class LeanPatchAuditEvidenceTests(unittest.TestCase):
    def test_complete_matching_coverage_is_accepted(self):
        pairs, severe = validate_audit_documents(
            doc([{"id": "ProDotNetZip", "resolvedVersion": "1.20.0"}]), doc([])
        )
        self.assertIn(("ProDotNetZip", "1.20.0"), pairs)
        self.assertEqual(severe, [])

    def test_clean_vulnerable_output_may_omit_frameworks(self):
        pairs, severe = validate_audit_documents(
            doc([{"id": "ProDotNetZip", "resolvedVersion": "1.20.0"}]),
            doc(include_framework=False),
        )
        self.assertIn(("ProDotNetZip", "1.20.0"), pairs)
        self.assertEqual(severe, [])

    def test_empty_object_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_audit_documents(doc(), {})

    def test_framework_coverage_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_audit_documents(doc(), doc(framework="net9.0"))

    def test_truncated_framework_package_evidence_is_rejected(self):
        vulnerable = doc()
        del vulnerable["projects"][0]["frameworks"][0]["topLevelPackages"]
        with self.assertRaises(ValueError):
            validate_audit_documents(doc(), vulnerable)

    def test_reported_problem_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_audit_documents(doc(), doc(problems=["advisory service unavailable"]))

    def test_high_severity_is_preserved_for_main_gate(self):
        vuln_doc = doc([{
            "id": "Example",
            "resolvedVersion": "1.0.0",
            "vulnerabilities": [{"severity": "High"}],
        }])
        _, severe = validate_audit_documents(
            doc([{"id": "ProDotNetZip", "resolvedVersion": "1.20.0"}]), vuln_doc
        )
        self.assertEqual(len(severe), 1)

    def test_unknown_vulnerability_severity_is_rejected(self):
        vuln_doc = doc([{
            "id": "Example",
            "resolvedVersion": "1.0.0",
            "vulnerabilities": [{"severity": "Unknown"}],
        }])
        with self.assertRaises(ValueError):
            validate_audit_documents(
                doc([{"id": "ProDotNetZip", "resolvedVersion": "1.20.0"}]), vuln_doc
            )

    def test_missing_vulnerability_severity_is_rejected(self):
        vuln_doc = doc([{
            "id": "Example",
            "resolvedVersion": "1.0.0",
            "vulnerabilities": [{}],
        }])
        with self.assertRaises(ValueError):
            validate_audit_documents(
                doc([{"id": "ProDotNetZip", "resolvedVersion": "1.20.0"}]), vuln_doc
            )


if __name__ == "__main__":
    unittest.main()
