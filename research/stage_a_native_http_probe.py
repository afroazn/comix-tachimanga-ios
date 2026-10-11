"""Stage A: inspect a Comix HTML response without executing JavaScript.

Research-only tool; NOT an extension, signing implementation or WebView replacement.
The optional live request fetches one ordinary public HTTPS page and prints only
structural indicators. No tokens, API signatures, cookies or chapter text are logged.
"""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ALLOWED_HOSTS = {"comix.to", "comix.ws"}
MAX_BODY_BYTES = 1024 * 1024


class InitialDataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._inside_initial_data = False
        self._parts: list[str] = []
        self.found = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script" and dict(attrs).get("id") == "initial-data":
            self._inside_initial_data = True
            self.found = True

    def handle_data(self, data: str) -> None:
        if self._inside_initial_data:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script":
            self._inside_initial_data = False

    @property
    def data(self) -> str:
        return "".join(self._parts)


def _chapter_items(value: object) -> int:
    """Recognize the chapter DTO used upstream; reject unrelated manga lists."""
    if not isinstance(value, dict):
        return 0
    payload = value.get("result", value)
    if not isinstance(payload, dict):
        return 0
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return 0
    if not all(
        isinstance(item, dict)
        and isinstance(item.get("id"), int)
        and not isinstance(item.get("id"), bool)
        and isinstance(item.get("number"), (int, float))
        and not isinstance(item.get("number"), bool)
        for item in items
    ):
        return 0
    return len(items)


def inspect_html(html: str) -> dict[str, object]:
    """Report only structural information; avoid recording manga details."""
    parser = InitialDataParser()
    parser.feed(html)
    summary: dict[str, object] = {
        "initial_data_found": parser.found,
        "valid_json": False,
        "query_count": 0,
        "chapter_list_candidates": 0,
        "chapter_items_seen": 0,
    }
    if not parser.data:
        return summary
    try:
        obj = json.loads(parser.data)
    except ValueError:
        return summary
    if not isinstance(obj, dict):
        return summary
    summary["valid_json"] = True
    queries = obj.get("queries")
    if not isinstance(queries, dict):
        return summary
    summary["query_count"] = len(queries)
    chapter_counts = [_chapter_items(value) for value in queries.values()]
    summary["chapter_list_candidates"] = sum(n > 0 for n in chapter_counts)
    summary["chapter_items_seen"] = sum(chapter_counts)
    return summary


def fetch_public_html(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("Only HTTPS URLs on comix.to or comix.ws are allowed")
    req = Request(
        url,
        headers={"User-Agent": "Comix-StageA-Research/0.1 (+manual diagnostic)"},
    )
    with urlopen(req, timeout=15) as response:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("Redirected outside the approved Comix domains")
        data = response.read(MAX_BODY_BYTES + 1)
        if len(data) > MAX_BODY_BYTES:
            raise ValueError("Response exceeds 1 MiB diagnostic limit")
        return data.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--html-file", help="Analyze an offline HTML fixture")
    group.add_argument("--url", help="Perform one HTTPS GET for a public Comix HTML page")
    args = parser.parse_args()
    try:
        if args.html_file:
            with open(args.html_file, encoding="utf-8") as handle:
                html = handle.read(MAX_BODY_BYTES + 1)
            if len(html.encode("utf-8")) > MAX_BODY_BYTES:
                raise ValueError("HTML fixture exceeds 1 MiB")
        else:
            html = fetch_public_html(args.url)
        print(json.dumps(inspect_html(html), indent=2, sort_keys=True))
        return 0
    except Exception as error:
        print(f"Probe inconclusive: {type(error).__name__}: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
