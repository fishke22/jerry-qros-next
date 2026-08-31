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
