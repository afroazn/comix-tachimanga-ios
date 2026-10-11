"""No-network fixture tests for public JS structural probe."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from stage_a_public_js_probe import ScriptFinder, inspect_js


class PublicJsProbeTests(unittest.TestCase):
    def test_module_scripts_found(self):
        f = ScriptFinder()
        f.feed(
            '<script src="/dist/main-abc123.js" type="module"></script>'
            '<script src="/other.js"></script>'
        )
        self.assertEqual(f.modules, ["/dist/main-abc123.js"])

    def test_static_imports_and_expected_atob_sizes(self):
        import base64
        literal = base64.b64encode(bytes(range(24))).decode("ascii")
        source = 'import {x} from "./feature.js"; const a = atob("' + literal + '");'
        result = inspect_js(source)
        self.assertEqual(result["imports"], ["feature.js"])
        self.assertEqual(result["static_atob_expected_length_counts"], {"24": 1})

    def test_counts_do_not_disclose_values(self):
        result = inspect_js('const a = "private-value"; import("./lazy.js");')
        self.assertEqual(result["imports"], ["lazy.js"])
        self.assertNotIn("private-value", str(result))

    def test_no_function_execution(self):
        result = inspect_js('throw new Error("must not execute");')
        self.assertEqual(result["imports"], [])
        self.assertEqual(result["atob_mentions"], 0)


if __name__ == "__main__":
    unittest.main()
