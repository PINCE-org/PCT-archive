#!/usr/bin/env python3
"""Build the search index for the static site.

Walks every `tables/**/*.json` sidecar and writes `site/index.json`, the data the
search page loads. Each entry carries the metadata plus the repo-relative path to
the `.pct` so the site can build a download link.
"""

import json
import os

TABLES_DIR = "tables"
OUTPUT = os.path.join("site", "index.json")


def main() -> None:
    entries = []
    for root, _dirs, files in os.walk(TABLES_DIR):
        for name in sorted(files):
            if not name.endswith(".json"):
                continue
            json_path = os.path.join(root, name)
            pct_path = json_path[: -len(".json")] + ".pct"
            if not os.path.exists(pct_path):
                continue  # skip orphaned sidecar
            with open(json_path, "r", encoding="utf-8") as fh:
                meta = json.load(fh)
            meta["pct_path"] = pct_path.replace(os.sep, "/")
            entries.append(meta)

    entries.sort(key=lambda e: (e.get("game", "").lower(), e.get("title", "").lower()))

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as fh:
        json.dump({"tables": entries}, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"Wrote {len(entries)} entries to {OUTPUT}")


if __name__ == "__main__":
    main()
