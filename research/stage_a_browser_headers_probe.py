"""One bounded test: do ordinary browser-identification headers alone change access?

A successful HTTP request would still need valid chapter JSON to prove chapter
access; a 403 is evidence ONLY for this exact test environment and request.
No cookies, signature emulation, challenge solving, hidden headers, or retries.
"""
from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL = (
    "https://comix.ws/api/v1/manga/rrglg/chapters"
    "?limit=1&order%5Bnumber%5D=desc&page=1"
)
PUBLIC_TITLE = "https://comix.ws/title/rrglg-the-great-journey-of-teenagers-folly-of-youths-arc"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 "
        "Mobile/15E148 Safari/604.1"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": PUBLIC_TITLE,
}

def check() -> dict[str, object]:
    request = Request(URL, headers=HEADERS)
    try:
        with urlopen(request, timeout=15) as response:
            body = response.read(256 * 1024)
            result = {
                "http_status": response.status,
                "parsed_chapters": False,
                "encrypted_response": False,
            }
            try:
                obj = json.loads(body)
                if isinstance(obj, dict):
                    data = obj.get("result")
                    result["parsed_chapters"] = (
                        isinstance(data, dict) and isinstance(data.get("items"), list)
                    )
                    result["encrypted_response"] = isinstance(obj.get("e"), str)
            except (ValueError, UnicodeDecodeError):
                pass
            return result
    except HTTPError as error:
        return {"http_status": error.code, "parsed_chapters": False}
    except URLError as error:
        return {"transport_error": type(error.reason).__name__, "parsed_chapters": False}

if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True, indent=2))
