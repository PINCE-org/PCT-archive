<!--
  This template is for submitting a cheat table.
  Contributing code, docs, or site changes instead? Delete this template and describe your change.

  To submit a table, upload a single .pct file into tables/<Game Name>/.
  Don't add a .json file, it's generated automatically from the metadata below when the PR is merged.

  Fill in the block below, keeping it inside the ```yaml fence.
  A bot will check it and reply here with anything that needs fixing.
-->

## Table metadata

```yaml
# Required
game:          # e.g. Stardew Valley
title:         # what the table does, e.g. Infinite Money + Energy
version:       # game build the table targets, e.g. 1.6.8

# Recommended (leave blank if unknown)
distributor:   # Steam / Epic / GOG / itch / retail / ...
runtime:       # native / proton / wine
binary_sha256: # sha256 of the game binary
author:        # name or handle of the author
```

## Checklist
- [ ] I added exactly one `.pct` file under `tables/<Game Name>/`
- [ ] I did **not** add a `.json` file (it is generated on merge)
- [ ] The `game`, `title`, and `version` fields above are filled in
- [ ] The table contains no obfuscated or malicious scripts
