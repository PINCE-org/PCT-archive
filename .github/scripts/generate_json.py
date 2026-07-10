#!/usr/bin/env python3
"""Generate the `.json` sidecar for a merged submission.

Runs after a PR is merged. Reads the metadata from the merged PR body and the
`.pct` that now lives on the default branch, then writes the matching sidecar
next to it (with `pct_version` copied from the `.pct` itself).

Prints the generated sidecar path on success so the workflow can commit it.

Environment:
    GH_TOKEN   token with read access to the pull request
    REPO       "owner/name" of the base repo
    PR_NUMBER  merged pull request number
    PR_BODY    merged pull request description
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from common import parse_metadata_block, sidecar_from_metadata, validate_metadata, validate_pct

API = "https://api.github.com"


def gh_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main() -> int:
    repo = os.environ["REPO"]
    pr = os.environ["PR_NUMBER"]
    body = os.environ.get("PR_BODY", "")

    # Locate the added .pct from the PR file list.
    files = gh_json(f"{API}/repos/{repo}/pulls/{pr}/files?per_page=100")
    pct_files = [f for f in files if f["status"] == "added" and f["filename"].endswith(".pct")]
    if len(pct_files) != 1:
        print(f"Expected exactly one added .pct, found {len(pct_files)}. Skipping.", file=sys.stderr)
        return 1
    pct_path = pct_files[0]["filename"]

    # The merged .pct is now checked out on the default branch.
    with open(pct_path, "r", encoding="utf-8") as fh:
        content = json.load(fh)
    if validate_pct(content):
        print("Merged .pct failed validation. Skipping sidecar generation.", file=sys.stderr)
        return 1

    meta = parse_metadata_block(body)
    if validate_metadata(meta):
        print("Merged PR metadata failed validation. Skipping sidecar generation.", file=sys.stderr)
        return 1

    sidecar = sidecar_from_metadata(meta, content["version"])
    json_path = pct_path[: -len(".pct")] + ".json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(json_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
