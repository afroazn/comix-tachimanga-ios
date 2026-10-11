"""Inspect how Comix's public 'secure' modules call atob, without executing JS.

Reports only syntactic categories; DOES NOT extract values, signatures, secrets
or response bodies. One public title-page GET + main bundle + secure bundles.
"""

from __future__ import annotations

import argparse
import json
import re
from urllib.parse import urljoin

from stage_a_public_js_probe import ScriptFinder, fetch, inspect_js


def argument_categories(source: str) -> dict[str, int]:
    kinds: dict[str, int] = {}
    for match in re.finditer(r"\batob\s*\(\s*", source):
        rest = source[match.end():match.end() + 120].lstrip()
        if not rest:
            kind = "unknown"
        elif rest[0] in "'\"":
            kind = "string_literal"
        elif re.match(r"[A-Za-z_$][\w$]*\s*\(", rest):
            kind = "function_call"
        elif re.match(r"[A-Za-z_$][\w$]*\s*[.\[]", rest):
            kind = "property_or_index"
        elif re.match(r"[A-Za-z_$][\w$]*", rest):
            kind = "identifier_or_expression"
        else:
            kind = "other_expression"
        kinds[kind] = kinds.get(kind, 0) + 1
    return kinds


def analyze_secure(title_url: str) -> dict[str, object]:
    parser = ScriptFinder()
    parser.feed(fetch(title_url))
    main = next((urljoin(title_url, src) for src in parser.modules if "/dist/main-" in src), None)
    result: dict[str, object] = {"main_found": bool(main), "secure_modules": [], "errors": []}
    if not main:
        return result
    main_source = fetch(main)
    imports = inspect_js(main_source)["imports"]
    secure_names = [name for name in imports if "secure-" in name][:5]
    for name in secure_names:
        try:
            source = fetch(urljoin(main, name))
            stats = inspect_js(source)
            result["secure_modules"].append({
                "file": name.rsplit("/", 1)[-1],
                "atob_mentions": stats["atob_mentions"],
                "static_expected_length_literals": stats["static_atob_expected_length_counts"],
                "argument_categories": argument_categories(source),
            })
        except Exception as error:
            result["errors"].append(name.rsplit("/", 1)[-1] + ": " + type(error).__name__)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(analyze_secure(args.url), indent=2, sort_keys=True))
    except Exception as error:
        print(json.dumps({"inconclusive": type(error).__name__ + ": " + str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
