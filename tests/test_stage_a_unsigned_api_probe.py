"""Offline tests for signed-API feasibility probe. No external requests."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from stage_a_unsigned_api_probe import api_url, summarize_api_reply


class StageAUnsignedApiTests(unittest.TestCase):
    def test_endpoint_uses_public_id_and_unsigned_query(self):
        url = api_url("comix.ws", "rrglg")
        self.assertIn("/api/v1/manga/rrglg/chapters", url)
        self.assertIn("limit=1", url)
        self.assertNotIn("_=", url)

    def test_invalid_host_is_refused(self):
        with self.assertRaises(ValueError):
            api_url("example.com", "abc")

    def test_invalid_id_is_refused(self):
        with self.assertRaises(ValueError):
            api_url("comix.to", "../admin")

    def test_encrypted_body_is_not_treated_as_chapters(self):
        result = summarize_api_reply(200, json.dumps({"e": "SYNTHETIC-ENCRYPTED"}).encode())
        self.assertEqual(result["chapter_items"], 0)
        self.assertTrue(result["encrypted_payload"])

    def test_cleartext_chapter_list_shape(self):
        body = json.dumps({"result": {"items": [{"id": 1, "number": 2}]}}).encode()
        result = summarize_api_reply(200, body)
        self.assertEqual(result["chapter_items"], 1)
        self.assertFalse(result["encrypted_payload"])


if __name__ == "__main__":
    unittest.main()
