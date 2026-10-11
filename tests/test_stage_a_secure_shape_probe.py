"""Offline tests for a syntax-only secure-module diagnostic."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from stage_a_secure_shape_probe import argument_categories


class StageASecureShapeTests(unittest.TestCase):
    def test_identifies_expression_categories(self):
        source = (
            'atob(x); atob(compute()); atob(obj.value); '
            'atob("abc"); atob(window[key]);'
        )
        actual = argument_categories(source)
        self.assertEqual(actual, {
            "identifier_or_expression": 1,
            "function_call": 1,
            "property_or_index": 2,
            "string_literal": 1,
        })

    def test_no_decoder_calls(self):
        self.assertEqual(argument_categories("const hello = 1;"), {})


if __name__ == "__main__":
    unittest.main()
