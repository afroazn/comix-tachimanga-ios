"""Offline regression tests for the read-only Stage A HTML probe.

Synthetic fixtures only. These do NOT establish that live Comix works on iOS.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from stage_a_native_http_probe import fetch_public_html, inspect_html


def html_with_queries(queries):
    payload = json.dumps({"queries": queries})
    return f'<html><head><script id="initial-data">{payload}</script></head></html>'


class StageANativeProbeTests(unittest.TestCase):
    def test_valid_chapter_list_in_initial_data(self):
        doc = html_with_queries({
            '["chapters",123]': {
                "result": {
                    "items": [
                        {"id": 101, "number": 1},
                        {"id": 102, "number": 2.5},
                    ],
                },
            },
        })
        self.assertEqual(
            inspect_html(doc),
            {
                "initial_data_found": True,
                "valid_json": True,
                "query_count": 1,
                "chapter_list_candidates": 1,
                "chapter_items_seen": 2,
            },
        )

    def test_direct_items_are_recognized(self):
        doc = html_with_queries({"chapters": {"items": [{"id": 10, "number": 5}]}})
        self.assertEqual(inspect_html(doc)["chapter_items_seen"], 1)

    def test_browse_results_are_not_misidentified_as_chapters(self):
        doc = html_with_queries({
            "browse": {"result": {"items": [{"id": 123, "title": "Synthetic example"}]}},
        })
        self.assertEqual(inspect_html(doc)["chapter_list_candidates"], 0)

    def test_boolean_id_not_mistaken_for_integer(self):
        doc = html_with_queries({"chapters": {"result": {"items": [{"id": True, "number": 1}]}}})
        self.assertEqual(inspect_html(doc)["chapter_items_seen"], 0)

    def test_partial_chapter_objects_are_rejected(self):
        doc = html_with_queries({"chapters": {"result": {"items": [{"id": 1}]}}})
        self.assertEqual(inspect_html(doc)["chapter_items_seen"], 0)

    def test_missing_initial_data_reports_no_evidence(self):
        result = inspect_html("<html><body>ordinary page</body></html>")
        self.assertFalse(result["initial_data_found"])
        self.assertEqual(result["chapter_items_seen"], 0)

    def test_invalid_initial_data_does_not_crash(self):
        result = inspect_html('<script id="initial-data">{invalid}</script>')
        self.assertTrue(result["initial_data_found"])
        self.assertFalse(result["valid_json"])

    def test_missing_queries_not_assumed_to_contain_chapters(self):
        result = inspect_html('<script id="initial-data">{"other":true}</script>')
        self.assertTrue(result["valid_json"])
        self.assertEqual(result["query_count"], 0)

    def test_other_hosts_are_rejected_before_any_network_call(self):
        with self.assertRaises(ValueError):
            fetch_public_html("https://example.org/title/123")
        with self.assertRaises(ValueError):
            fetch_public_html("http://comix.to/browse")


if __name__ == "__main__":
    unittest.main()
