import tempfile
import unittest
from pathlib import Path

from qros_lean.runtime_overlay import (
    COMPRESSION_NEW,
    COMPRESSION_OLD,
    MESSAGING_ITEM_NEW,
    MESSAGING_ITEM_OLD,
    MESSAGING_NETMQ_OLD,
    PATCH_MODE,
    expected_patched_texts,
    overlay_identity,
    patch_implementation_hash,
)


class LeanRuntimeOverlayTests(unittest.TestCase):
    def test_expected_patch_is_exact_and_deterministic(self):
        compression = "<Project>\n" + COMPRESSION_OLD + "\n</Project>\n"
        messaging = "<Project>\n" + MESSAGING_NETMQ_OLD + MESSAGING_ITEM_OLD + "\n</Project>\n"
        patched_compression, patched_messaging = expected_patched_texts(compression, messaging)
        self.assertIn(COMPRESSION_NEW, patched_compression)
        self.assertNotIn(COMPRESSION_OLD, patched_compression)
        self.assertNotIn("NetMQ", patched_messaging)
        self.assertIn(MESSAGING_ITEM_NEW, patched_messaging)

    def test_missing_or_duplicate_anchor_fails_closed(self):
        with self.assertRaises(RuntimeError):
            expected_patched_texts("<Project/>", "<Project/>")
        with self.assertRaises(RuntimeError):
            expected_patched_texts(
                COMPRESSION_OLD + "\n" + COMPRESSION_OLD,
                MESSAGING_NETMQ_OLD + MESSAGING_ITEM_OLD,
            )

    def test_patch_identity_changes_when_implementation_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            wrapper = root / "scripts" / "apply_lean_security_patch.py"
            implementation = root / "src" / "qros_lean" / "runtime_overlay.py"
            wrapper.parent.mkdir(parents=True)
            implementation.parent.mkdir(parents=True)
            wrapper.write_text("wrapper-v1\n", encoding="utf-8")
            implementation.write_text("implementation-v1\n", encoding="utf-8")
            first = patch_implementation_hash(root)
            implementation.write_text("implementation-v2\n", encoding="utf-8")
            second = patch_implementation_hash(root)
            self.assertNotEqual(first, second)

    def test_overlay_identity_changes_with_runtime_bytes(self):
        base = {
            "mode": PATCH_MODE,
            "patch_script_hash": "sha256:" + "a" * 64,
            "patched_graph_hash": "sha256:" + "b" * 64,
            "launcher_assembly_hash": "sha256:" + "c" * 64,
            "runtime_assembly_manifest_hash": "sha256:" + "e" * 64,
            "runtime_assembly_count": "3",
        }
        changed = dict(base)
        changed["launcher_assembly_hash"] = "sha256:" + "d" * 64
        changed_manifest = dict(base)
        changed_manifest["runtime_assembly_manifest_hash"] = "sha256:" + "f" * 64
        self.assertNotEqual(overlay_identity(base), overlay_identity(changed))
        self.assertNotEqual(overlay_identity(base), overlay_identity(changed_manifest))

    def test_overlay_identity_rejects_less_than_three_runtime_assemblies(self):
        overlay = {
            "mode": PATCH_MODE,
            "patch_script_hash": "sha256:" + "a" * 64,
            "patched_graph_hash": "sha256:" + "b" * 64,
            "launcher_assembly_hash": "sha256:" + "c" * 64,
            "runtime_assembly_manifest_hash": "sha256:" + "d" * 64,
            "runtime_assembly_count": "2",
        }
        with self.assertRaises(RuntimeError):
            overlay_identity(overlay)


if __name__ == "__main__":
    unittest.main()
