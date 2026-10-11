"""Synthetic no-network tests of Comix query-shape diagnostics."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from stage_a_query_shape_probe import describe_query_shapes


class StageAQueryShapeTests(unittest.TestCase):
    def test_structure_only_summary_of_chapter_payload(self):
        raw = json.dumps({
            "queries": {
                '["chapters",123]': {
                    "result": {
                        "items": [{"id": 5, "number": 1.0, "name": "Synthetic"}],
                        "pagination": {"page": 1},
                    },
                },
            },
        })
        result = describe_query_shapes('<script id="initial-data">' + raw + "</script>")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["result_list_fields"], {"items": 1})
        self.assertEqual(result[0]["first_item_fields"], ["id", "name", "number"])
        self.assertNotIn("Synthetic", str(result))

    def test_bad_html_returns_no_shapes(self):
        self.assertEqual(describe_query_shapes("<html>No queries</html>"), [])


if __name__ == "__main__":
    unittest.main()
