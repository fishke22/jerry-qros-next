import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import qros_lean_patch_experiment as patcher

ROOT = Path(__file__).resolve().parents[1]


class LeanPatchExperimentTests(unittest.TestCase):
    def test_authorization_remains_research_only(self):
        r=json.loads((ROOT/"config"/"lean-remediation-research.json").read_text(encoding="utf-8"))
        self.assertTrue(r["architecture_amendment_approved"])
        self.assertTrue(r["lean_source_patch_experiment_authorized"])
        self.assertFalse(r["runtime_promotion_allowed"])
        self.assertFalse(r["lean_fork_authorized"])
        self.assertFalse(r["lean_gitlink_change_authorized"])

    def test_compression_candidate_is_authorized_but_not_promotable(self):
        e=json.loads((ROOT/"config"/"lean-patch-experiment.json").read_text(encoding="utf-8"))
        candidate=e["candidates"]["COMPRESSION_SYSTEM_IO_MIGRATION"]
        self.assertTrue(candidate["implementation_authorized"])
        self.assertFalse(candidate["promotion_allowed"])
        self.assertFalse(e["combined_candidate"]["promotion_allowed"])

    def test_path_traversal_candidate_is_research_only(self):
        e=json.loads((ROOT/"config"/"lean-patch-experiment.json").read_text(encoding="utf-8"))
        c=e["source_hardening_candidates"]["COMPRESSION_PATH_TRAVERSAL"]
        self.assertEqual(c["rule"], "CA5389")
        self.assertTrue(c["implementation_authorized"])
        self.assertFalse(c["promotion_allowed"])

    def test_messaging_patch_is_exact_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.csproj"
            old='<PackageReference Include="NetMQ" Version="4.0.1.6" />'
            new='<PackageReference Include="NetMQ" Version="4.0.4.3" />'
            p.write_text(old+"\n",encoding="utf-8")
            cfg={"path":p,"old":old,"new":new}
            with patch.dict(patcher.CANDIDATES,{"messaging-netmq-4.0.4.3":cfg},clear=True):
                patcher.apply("messaging-netmq-4.0.4.3")
                self.assertEqual(p.read_text(encoding="utf-8").strip(),new)
                with self.assertRaises(RuntimeError):
                    patcher.apply("messaging-netmq-4.0.4.3")


if __name__=="__main__":
    unittest.main()
