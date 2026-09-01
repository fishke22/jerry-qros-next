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
    sha256_file,
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

    def test_patch_implementation_hash_is_actual_implementation_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            implementation = root / "src" / "qros_lean" / "runtime_overlay.py"
            implementation.parent.mkdir(parents=True)
            implementation.write_text("implementation-v1\n", encoding="utf-8")
            self.assertEqual(patch_implementation_hash(root), sha256_file(implementation))
            first = patch_implementation_hash(root)
            implementation.write_text("implementation-v2\n", encoding="utf-8")
            self.assertNotEqual(first, patch_implementation_hash(root))

    def test_overlay_identity_changes_with_runtime_or_patch_bytes(self):
        base = {
            "mode": PATCH_MODE,
            "patch_script_hash": "sha256:" + "a" * 64,
            "patch_implementation_hash": "sha256:" + "b" * 64,
            "patched_graph_hash": "sha256:" + "c" * 64,
            "launcher_assembly_hash": "sha256:" + "d" * 64,
            "runtime_assembly_manifest_hash": "sha256:" + "e" * 64,
            "runtime_assembly_count": "3",
        }
        changed_launcher = dict(base)
        changed_launcher["launcher_assembly_hash"] = "sha256:" + "f" * 64
        changed_impl = dict(base)
        changed_impl["patch_implementation_hash"] = "sha256:" + "9" * 64
        self.assertNotEqual(overlay_identity(base), overlay_identity(changed_launcher))
        self.assertNotEqual(overlay_identity(base), overlay_identity(changed_impl))

    def test_overlay_identity_rejects_less_than_three_runtime_assemblies(self):
        overlay = {
            "mode": PATCH_MODE,
            "patch_script_hash": "sha256:" + "a" * 64,
            "patch_implementation_hash": "sha256:" + "b" * 64,
            "patched_graph_hash": "sha256:" + "c" * 64,
            "launcher_assembly_hash": "sha256:" + "d" * 64,
            "runtime_assembly_manifest_hash": "sha256:" + "e" * 64,
            "runtime_assembly_count": "2",
        }
        with self.assertRaises(RuntimeError):
            overlay_identity(overlay)


if __name__ == "__main__":
    unittest.main()
