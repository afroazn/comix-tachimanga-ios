"""Static, read-only inspection of publicly delivered Comix JavaScript.

Purpose: identify HOW the website obtains/uses the six byte arrays that the
upstream extension captures inside WebView, without claiming a permanent key.

This tool intentionally DOES NOT execute JS, extract or print raw byte arrays,
make signed API requests, or attempt to evade access restrictions.
"""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin
from stage_a_public_js_probe import ScriptFinder, fetch, inspect_js

PUBLIC_TITLE = (
    "https://comix.ws/title/rrglg-the-great-journey-of-teenagers-folly-of-youths-arc"
)
KEYWORDS = (
    "atob",
    "crypto.subtle",
    "Uint8Array",
    "TextEncoder",
    "btoa",
    "chapters(",
    "/api/v1",
)
MAX_SNIPPETS = 8


def redacted_context(source: str, term: str, limit: int = 110, max_occurrences: int = 6) -> list[str]:
    """Short, non-executable excerpts around relevant identifiers, no raw strings."""
    out = []
    for m in list(re.finditer(re.escape(term), source))[:max_occurrences]:
        a = max(0, m.start() - limit)
        b = min(len(source), m.end() + limit)
        snippet = source[a:b]
        # Suppress literal data (including base64, paths, credentials).
        snippet = re.sub(r'"(?:[^"\\]|\\.)*"', '"[literal]"', snippet)
        snippet = re.sub(r"'(?:[^'\\]|\\.)*'", "'[literal]'", snippet)
        snippet = re.sub(r'(?<![A-Za-z0-9_])[A-Za-z0-9+/_=-]{72,}', "[long-token]", snippet)
        out.append(snippet[:300])
    return out


def analyze(title: str) -> dict:
    html = fetch(title)
    parser = ScriptFinder()
    parser.feed(html)
    main_url = next((urljoin(title, src) for src in parser.modules if "/dist/main-" in src), None)
    report = {
        "main_found": bool(main_url),
        "imports_count": 0,
        "imports_read": 0,
        "errors": [],
        "interesting_modules": [],
    }
    if not main_url:
        return report
    main_js = fetch(main_url)
    imports = inspect_js(main_js)["imports"]
    report["imports_count"] = len(imports)
    for name in imports[:40]:
        try:
            js = fetch(urljoin(main_url, name))
        except Exception as error:
            report["errors"].append(type(error).__name__ + " for " + name.rsplit("/", 1)[-1])
            continue
        report["imports_read"] += 1
        counts = {term: js.count(term) for term in KEYWORDS}
        if not (
            name.startswith("secure-")
            or counts["atob"] > 0
            or counts["/api/v1"] > 0
            or counts["chapters("] > 0
        ):
            continue
        # Print only the code shape and short redacted contexts.
        report["interesting_modules"].append({
            "file": name.rsplit("/", 1)[-1],
            "sha256_12": hashlib.sha256(js.encode()).hexdigest()[:12],
            "keyword_counts": {k: v for k, v in counts.items() if v},
            "atob_context": redacted_context(js, "atob", max_occurrences=4),
            "api_context": redacted_context(js, "/api/v1", max_occurrences=2),
            "chapter_call_context": redacted_context(js, "chapters(", max_occurrences=2),
        })
    return report


if __name__ == "__main__":
    try:
        print(json.dumps(analyze(PUBLIC_TITLE), indent=2, sort_keys=True))
    except Exception as error:
        print(json.dumps({"error": type(error).__name__ + ": " + str(error)}))
        raise SystemExit(2)
