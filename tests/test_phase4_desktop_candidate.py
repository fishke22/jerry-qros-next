import unittest

from scripts.validate_phase4_desktop_candidate import validate_static


class Phase4DesktopCandidateStaticTests(unittest.TestCase):
    def test_candidate_static_boundary(self):
        validate_static()


if __name__ == "__main__":
    unittest.main()
