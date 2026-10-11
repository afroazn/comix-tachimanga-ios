"""Research-only description of Comix script#initial-data query SHAPES.

No content values, tokens, image URLs, or manga text are printed. This diagnostic
is designed to distinguish hidden nested chapter data from unrelated query data.
"""

from __future__ import annotations

import argparse
import json
from stage_a_native_http_probe import InitialDataParser, fetch_public_html


def _keys(value):
    return sorted(str(k) for k in value.keys())[:30] if isinstance(value, dict) else []


def describe_query_shapes(html: str) -> list[dict[str, object]]:
    parser = InitialDataParser()
    parser.feed(html)
    if not parser.data:
        return []
    try:
        obj = json.loads(parser.data)
    except ValueError:
        return []
    queries = obj.get("queries") if isinstance(obj, dict) else None
    if not isinstance(queries, dict):
        return []
    results = []
    for index, (query_key, value) in enumerate(queries.items()):
        result = value.get("result") if isinstance(value, dict) else None
        entry: dict[str, object] = {
            "index": index,
            "query_key": str(query_key)[:120],
            "top_fields": _keys(value),
            "result_fields": _keys(result),
            "result_list_fields": {},
        }
        if isinstance(result, dict):
            entry["result_list_fields"] = {
                key: len(item)
                for key, item in result.items()
                if isinstance(item, list)
            }
            chapter_items = result.get("items")
            if isinstance(chapter_items, list) and chapter_items and isinstance(chapter_items[0], dict):
                entry["first_item_fields"] = _keys(chapter_items[0])
        results.append(entry)
    return results


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--url", required=True, help="One public Comix HTTPS title URL")
    args = cli.parse_args()
    try:
        shapes = describe_query_shapes(fetch_public_html(args.url))
        print(json.dumps(shapes, indent=2, sort_keys=True))
        return 0
    except Exception as error:
        print(f"Probe inconclusive: {type(error).__name__}: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
