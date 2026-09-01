import unittest

from qros_lean.runtime_overlay import (
    COMPRESSION_NEW,
    COMPRESSION_OLD,
    MESSAGING_ITEM_NEW,
    MESSAGING_ITEM_OLD,
    MESSAGING_NETMQ_OLD,
    PATCH_MODE,
    expected_patched_texts,
    overlay_identity,
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


if __name__ == "__main__":
    unittest.main()
