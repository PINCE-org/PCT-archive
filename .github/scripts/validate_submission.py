#!/usr/bin/env python3
"""Validate a cheat-table submission PR and write a Markdown report.

Runs under `pull_request_target`, so it must treat the submitted `.pct` strictly
as DATA: it is parsed as JSON and never executed. Only trusted scripts from the
base repo run here.

Writes `validation-report.md` (posted back as a sticky PR comment) and exits
non-zero if the submission is invalid, so the check turns red.

Environment:
    GH_TOKEN   token with read access to the pull request
    REPO       "owner/name" of the base repo
    PR_NUMBER  pull request number
    PR_BODY    pull request description
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from common import load_pct_bytes, parse_metadata_block, sidecar_from_metadata, validate_metadata, validate_pct

API = "https://api.github.com"


def gh(url: str, accept: str = "application/vnd.github+json") -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def get_added_files(repo: str, pr: str) -> list[dict]:
    """Return the list of files added by the PR (paginated)."""
    files, page = [], 1
    while True:
        batch = json.loads(gh(f"{API}/repos/{repo}/pulls/{pr}/files?per_page=100&page={page}"))
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return files


def find_existing_duplicate(meta: dict) -> str | None:
    """Return the path of an existing sidecar with the same game, title, and version.

    Scans the base branch checkout, which holds the already merged tables. The
    submitted table isn't present here, so a match means a genuine duplicate.

    Args:
        meta: Metadata parsed from the PR body.

    Returns:
        str | None: Repo-relative path of the clashing sidecar, or None if unique.
    """

    def norm(value):
        return (value or "").strip().lower()

    target = (norm(meta.get("game")), norm(meta.get("title")), norm(meta.get("version")))
    for root, _dirs, files in os.walk("tables"):
        for name in files:
            if not name.endswith(".json"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    existing = json.load(fh)
            except Exception:
                continue
            if (norm(existing.get("game")), norm(existing.get("title")), norm(existing.get("version"))) == target:
                return path.replace(os.sep, "/")
    return None


def main() -> int:
    repo = os.environ["REPO"]
    pr = os.environ["PR_NUMBER"]
    body = os.environ.get("PR_BODY", "")

    errors: list[str] = []
    notes: list[str] = []

    # 1. File-shape checks: exactly one added .pct under tables/, no .json, no overwrite.
    files = get_added_files(repo, pr)
    added = [f for f in files if f["status"] == "added"]
    pct_files = [f for f in added if f["filename"].endswith(".pct")]
    modified_pct = [f for f in files if f["status"] == "modified" and f["filename"].endswith(".pct") and f["filename"].startswith("tables/")]
    json_files = [f for f in files if f["filename"].endswith(".json") and f["filename"].startswith("tables/")]

    if json_files:
        errors.append("Please don't add a `.json` file. It's generated automatically on merge.")

    # A re-upload to an existing path shows up as "modified" rather than "added".
    for f in modified_pct:
        errors.append(
            f"`{f['filename']}` already exists in the archive, so this would overwrite it. "
            f"If you're updating that table, say so in the description so a maintainer can review the change. "
            f"If it's a different table, rename your file so it doesn't replace the existing one."
        )

    if len(pct_files) == 0 and not modified_pct:
        errors.append("No `.pct` file was added. Upload exactly one table under `tables/<Game Name>/`.")
    elif len(pct_files) > 1:
        errors.append(f"Found {len(pct_files)} `.pct` files. Please submit one table per pull request.")

    for f in pct_files:
        if not f["filename"].startswith("tables/") or f["filename"].count("/") < 2:
            errors.append(f"`{f['filename']}` must live under `tables/<Game Name>/<table>.pct`.")

    # 2. Metadata checks.
    meta = parse_metadata_block(body)
    if not meta:
        errors.append("Couldn't find the metadata block. Fill in the ```yaml block in the PR description.")
    errors.extend(validate_metadata(meta))

    # 2b. Reject an exact duplicate of an existing table (same game, title, version).
    if all(meta.get(k) for k in ("game", "title", "version")):
        duplicate = find_existing_duplicate(meta)
        if duplicate:
            errors.append(
                f"A table with the same game, title, and version already exists: `{duplicate}`. "
                f"If this is a different table, change the title or version to tell them apart."
            )

    # 3. Validate the .pct contents (data only, never executed).
    pct_version = None
    if len(pct_files) == 1:
        raw = gh(pct_files[0]["contents_url"], accept="application/vnd.github.raw")
        content, load_err = load_pct_bytes(raw)
        if load_err:
            errors.append(load_err)
        else:
            pct_errors = validate_pct(content)
            errors.extend(pct_errors)
            if not pct_errors:
                pct_version = content["version"]
                notes.append(f"`.pct` is valid (format v{pct_version}).")

    # 4. Build the report.
    lines = ["## Submission check", ""]
    if errors:
        lines.append("❌ **Please fix the following before this can be merged:**")
        lines.append("")
        lines += [f"- {e}" for e in errors]
    else:
        lines.append("✅ **Looks good!** A maintainer will review the table and merge it.")
        lines.append("")
        lines.append("On merge, this metadata sidecar will be generated:")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(sidecar_from_metadata(meta, pct_version), indent=2, ensure_ascii=False))
        lines.append("```")
    for n in notes:
        lines.append(f"\n> {n}")

    with open("validation-report.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
