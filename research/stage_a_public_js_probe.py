"""Inspect publicly delivered Comix JS module *structure* without executing JavaScript.

This is a bounded read-only diagnostic, not a signing-key extractor.
It prints counts and file names only, never payloads, keys, chapter contents,
or user credentials. It does not try to defeat access controls.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter
from html.parser import HTMLParser
import json
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

MAX_JS_BYTES = 2 * 1024 * 1024
ALLOWED_HOSTS = {"comix.ws", "comix.to"}
IMPORT_RE = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(\s*)["']\./([^"'?]+\.js)["']""")
ATOB_RE = re.compile(r"""\batob\s*\(\s*(["'])([A-Za-z0-9+/=_-]{20,16000})\1\s*\)""")


class ScriptFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.modules = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return
        d = dict(attrs)
        if d.get("type") == "module" and d.get("src"):
            self.modules.append(d["src"])


def inspect_js(source: str) -> dict[str, object]:
    chunks = list(dict.fromkeys(IMPORT_RE.findall(source)))
    length_categories = Counter()
    for _, value in ATOB_RE.findall(source):
        try:
            decoded = base64.b64decode(value + "=" * ((-len(value)) % 4), validate=True)
        except ValueError:
            continue
        if len(decoded) in (24, 32, 256):
            length_categories[str(len(decoded))] += 1
    return {
        "imports": chunks,
        "atob_mentions": len(re.findall(r"\batob\b", source)),
        "static_atob_expected_length_counts": dict(length_categories),
        "chapters_mentions": len(re.findall(r"\bchapters\b", source)),
        "js_bytes": len(source.encode("utf-8")),
    }


def fetch(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("URL must use HTTPS and an approved Comix host")
    req = Request(url, headers={"User-Agent": "Comix-StageA-Research/0.1"})
    with urlopen(req, timeout=15) as resp:
        final = urlparse(resp.geturl())
        if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
            raise ValueError("Redirected outside approved Comix hosts")
        data = resp.read(MAX_JS_BYTES + 1)
        if len(data) > MAX_JS_BYTES:
            raise ValueError("Response exceeds read limit")
        return data.decode("utf-8", errors="replace")


def analyze(html_url: str, max_chunks: int = 10) -> dict[str, object]:
    parser = ScriptFinder()
    parser.feed(fetch(html_url))
    main = next(
        (urljoin(html_url, src) for src in parser.modules if "/dist/main-" in src),
        None,
    )
    result: dict[str, object] = {
        "module_script_count": len(parser.modules),
        "main_script_found": main is not None,
        "main": None,
        "chunks": [],
        "errors": [],
    }
    if not main:
        return result
    try:
        main_stats = inspect_js(fetch(main))
    except Exception as error:
        result["errors"].append("main: " + type(error).__name__ + ": " + str(error))
        return result
    result["main"] = {
        key: value
        for key, value in main_stats.items()
        if key != "imports"
    }
    result["main"]["imports_count"] = len(main_stats["imports"])
    for name in main_stats["imports"][:max_chunks]:
        url = urljoin(main, name)
        try:
            stats = inspect_js(fetch(url))
            result["chunks"].append({
                "file": name.rsplit("/", 1)[-1],
                "atob_mentions": stats["atob_mentions"],
                "static_atob_expected_length_counts": stats["static_atob_expected_length_counts"],
                "chapters_mentions": stats["chapters_mentions"],
                "js_bytes": stats["js_bytes"],
            })
        except Exception as error:
            result["errors"].append(
                name.rsplit("/", 1)[-1] + ": " + type(error).__name__
            )
    return result


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--url", required=True)
    arg.add_argument("--max-chunks", type=int, default=10)
    opts = arg.parse_args()
    if not 0 <= opts.max_chunks <= 10:
        arg.error("max-chunks must be between 0 and 10")
    try:
        print(json.dumps(analyze(opts.url, opts.max_chunks), indent=2))
    except Exception as error:
        print(json.dumps({"inconclusive_error": type(error).__name__ + ": " + str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
