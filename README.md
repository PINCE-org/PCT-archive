# PCT-archive

A community database of **PINCE cheat tables** (`.pct` files), open for anyone to browse and download.

- 🔎 **Search & browse:** https://pince-org.github.io/PCT-archive/
- ➕ **Contribute a table:** see [CONTRIBUTING.md](CONTRIBUTING.md)

## What's in here

```
tables/<Game Name>/<table>.pct    the cheat table (this is what you download)
tables/<Game Name>/<table>.json   metadata (auto-generated on merge)
```

Every table is tied to a specific game **build**, so the metadata records the
`version` (and, when known, `distributor`, `runtime`, and the binary hash) it
was made for. Different game versions live as separate `.pct` files in the same
game folder.

## How it works

1. A contributor opens a PR that adds a single `.pct`, filling the metadata block
   in the PR template.
2. CI validates the `.pct` and the metadata, and comments on the PR with anything
   that needs fixing.
3. A maintainer reviews the table (including any embedded scripts) and merges.
4. On merge, the matching `.json` sidecar is generated and the search site is rebuilt.

## Safety

Cheat tables can embed scripts that run inside PINCE with debugging privileges.
Every submission is reviewed before merge. Only download tables you're willing to
inspect, and prefer tables whose `version` or `binary_sha256` matches your own game binary.
