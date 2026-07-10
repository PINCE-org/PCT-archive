"""Shared helpers for PCT-archive automation.

Kept dependency-free (standard library only) so the workflows need no pip installs.
The `.pct` validation mirrors PINCE's `is_valid_session_data` (GUI/Session/session.py).
Keep the two in sync when the session format changes.
"""

import json
import re

MANDATORY_FIELDS = ["game", "title", "version"]
OPTIONAL_FIELDS = ["distributor", "runtime", "binary_sha256", "author"]

# The metadata block in a PR body is a flat ```yaml fence of `key: value` lines.
_YAML_FENCE = re.compile(r"```ya?ml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def parse_metadata_block(pr_body: str) -> dict[str, str]:
    """Extract the first ```yaml fenced block from a PR body into a flat dict.

    Comments (`# ...`) and blank values are dropped, so unfilled optional fields
    simply don't appear in the result.

    Args:
        pr_body: The full pull request description.

    Returns:
        dict[str, str]: Filled-in metadata fields.
    """
    if not pr_body:
        return {}
    match = _YAML_FENCE.search(pr_body)
    if not match:
        return {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.split("#", 1)[0].strip()  # strip inline comments
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key and value:
            meta[key] = value
    return meta


def validate_metadata(meta: dict[str, str]) -> list[str]:
    """Return a list of human-readable problems with the metadata (empty if valid)."""
    errors = []
    for field in MANDATORY_FIELDS:
        if not meta.get(field):
            errors.append(f"`{field}` is required but missing or empty")
    runtime = meta.get("runtime", "").lower()
    if runtime and runtime not in ("native", "proton", "wine"):
        errors.append(f"`runtime` should be one of native/proton/wine, got `{meta['runtime']}`")
    sha = meta.get("binary_sha256", "")
    if sha and not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
        errors.append("`binary_sha256` must be a 64-character hex sha256 if provided")
    return errors


def validate_pct(content) -> list[str]:
    """Validate the structure of a parsed `.pct` file. Mirrors is_valid_session_data.

    Args:
        content: The JSON-parsed contents of a `.pct` file.

    Returns:
        list[str]: Human-readable problems (empty if the file is a valid session).
    """
    if not isinstance(content, dict):
        return ["`.pct` file is not a JSON object"]
    errors = []
    for key in ("version", "notes", "bookmarks", "address_tree", "process_name"):
        if key not in content:
            errors.append(f"`.pct` is missing the `{key}` field")
    if not isinstance(content.get("version"), int):
        errors.append("`.pct` `version` must be an integer")
    if not isinstance(content.get("bookmarks", {}), dict):
        errors.append("`.pct` `bookmarks` must be an object")
    if not isinstance(content.get("structures", {}), dict):
        errors.append("`.pct` `structures` must be an object")
    return errors


def load_pct_bytes(raw: bytes):
    """Parse `.pct` bytes as JSON, returning (content, error_message)."""
    try:
        return json.loads(raw.decode("utf-8")), None
    except Exception as exc:
        return None, f"`.pct` file is not valid JSON: {exc}"


def sidecar_from_metadata(meta: dict[str, str], pct_version: int) -> dict:
    """Build the ordered sidecar `.json` dict from validated metadata."""
    sidecar: dict = {}
    for field in MANDATORY_FIELDS + OPTIONAL_FIELDS:
        if meta.get(field):
            sidecar[field] = meta[field]
    sidecar["pct_version"] = pct_version
    return sidecar
