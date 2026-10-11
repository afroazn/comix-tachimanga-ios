"""Offline unit tests, with synthetic JS. No external requests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from inspect_public_key_origin import redacted_context


class KeyOriginStructureTests(unittest.TestCase):
    def test_context_never_exposes_complete_literal(self):
        source = 'window.atob("VERY-LONG-BASE64-DEMO-STRING"); const z = 1;'
        result = redacted_context(source, "atob")
        self.assertEqual(len(result), 1)
        self.assertIn("atob", result[0])
        self.assertNotIn("VERY-LONG", result[0])

    def test_no_occurrence(self):
        self.assertEqual(redacted_context('const x = 1;', 'atob'), [])


if __name__ == "__main__":
    unittest.main()
