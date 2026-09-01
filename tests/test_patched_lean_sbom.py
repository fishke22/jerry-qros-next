import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from qros_patched_lean_sbom import generate

class PatchedLeanSbomTests(unittest.TestCase):
    def test_generates_cyclonedx_and_license_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            packages=root/"packages"
            pkg=packages/"example.pkg"/"1.2.3"
            pkg.mkdir(parents=True)
            (pkg/"example.pkg.nuspec").write_text(
                '<package><metadata><license type="expression">MIT</license></metadata></package>',
                encoding="utf-8")
            digest=hashlib.sha512(b"package").digest()
            assets={
              "targets":{"net10.0":{"Example.Pkg/1.2.3":{"type":"package","dependencies":{}}}},
              "libraries":{"Example.Pkg/1.2.3":{"type":"package","sha512":base64.b64encode(digest).decode()}},
              "project":{"frameworks":{"net10.0":{"dependencies":{"Example.Pkg":{"target":"Package","version":"[1.2.3, )"}}}}}
            }
            ap=root/"project.assets.json";ap.write_text(json.dumps(assets),encoding="utf-8")
            sbom,report=generate(ap,packages)
            self.assertEqual(sbom["specVersion"],"1.7")
            self.assertEqual(len(sbom["components"]),1)
            self.assertEqual(sbom["components"][0]["licenses"],[{"expression":"MIT"}])
            self.assertTrue(report["promotion_ready"])
            self.assertEqual(report["license_status_counts"],{"EXPRESSION":1})

if __name__=="__main__": unittest.main()
