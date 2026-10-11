"""Stage A: test one normal, UNSIGNED GET to Comix's chapter API.

This does not generate signatures, obtain tokens, solve challenges, or decrypt
responses. It prints HTTP status and JSON *shape*, never copyrighted content.
An error status is a legitimate, inconclusive/negative research result.
"""

from __future__ import annotations

import argparse
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ALLOWED_HOSTS = {"comix.to", "comix.ws"}


def api_url(host: str, hid: str) -> str:
    if host not in ALLOWED_HOSTS:
        raise ValueError("Unapproved Comix hostname")
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", hid):
        raise ValueError("Invalid public manga identifier")
    params = urlencode({"limit": 1, "order[number]": "desc", "page": 1})
    return f"https://{host}/api/v1/manga/{hid}/chapters?{params}"


def summarize_api_reply(status: int, body: bytes) -> dict[str, object]:
    summary: dict[str, object] = {
        "http_status": status,
        "valid_json": False,
        "encrypted_payload": False,
        "chapter_items": 0,
        "top_level_fields": [],
    }
    try:
        root = json.loads(body)
    except (UnicodeDecodeError, ValueError):
        return summary
    if not isinstance(root, dict):
        return summary
    summary["valid_json"] = True
    summary["top_level_fields"] = sorted(root)[:15]
    summary["encrypted_payload"] = isinstance(root.get("e"), str)
    result = root.get("result")
    if isinstance(result, dict) and isinstance(result.get("items"), list):
        summary["chapter_items"] = len(result["items"])
    return summary


def run_probe(host: str, hid: str) -> dict[str, object]:
    url = api_url(host, hid)
    req = Request(
        url,
        headers={
            "User-Agent": "Comix-StageA-Research/0.1 (+manual diagnostic)",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(req, timeout=15) as response:
            return summarize_api_reply(response.status, response.read(256 * 1024))
    except HTTPError as error:
        # Report status only: no retry loops, challenge solving or body logging.
        return {"http_status": error.code, "valid_json": False, "chapter_items": 0}
    except URLError as error:
        return {"transport_error": str(error.reason), "valid_json": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=sorted(ALLOWED_HOSTS), required=True)
    parser.add_argument("--hid", required=True, help="Public manga hid from page metadata")
    args = parser.parse_args()
    print(json.dumps(run_probe(args.host, args.hid), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
