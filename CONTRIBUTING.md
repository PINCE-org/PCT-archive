# Contributing a cheat table

You can submit a cheat table easily via browser without needing Git or any developer tools.

## Submit a table (no Git required)

1. **Sign in** to GitHub (a free account is all you need).
2. Go to the [tables folder](../../tree/main/tables) and click
   **Add file → Upload files** (or use the **Submit a table** button on the
   [website](https://pince-org.github.io/PCT-archive/)).
3. **Drag in your `.pct` file.** Put it in a folder named after the game, e.g.
   `tables/Stardew Valley/infinite-money.pct`. Upload only the `.pct` and nothing else.
4. Click **Commit changes**. GitHub will offer to **create a fork and propose changes**. Accept it.
5. On the pull request screen, **fill in the metadata block** in the description.
6. Submit. A bot will check your submission and comment with anything to fix. A maintainer then reviews and merges it.

That's it. The `.json` metadata file is generated for you automatically.

## The metadata block

When you open the PR, the description is pre-filled with this. Fill the values inside the fence:

```yaml
# Required
game:          # e.g. Stardew Valley
title:         # what the table does, e.g. Infinite Money + Energy
version:       # game build the table targets, e.g. 1.6.8

# Recommended (leave as-is if unknown)
distributor:   # Steam / Epic / GOG / itch / retail / ...
runtime:       # native / proton / wine
binary_sha256: # sha256 of the game binary
author:        # name or handle of the author
```

## Rules
- One `.pct` per pull request.
- Don't add a `.json` file, it's generated on merge.
- No obfuscated or malicious scripts. Tables are reviewed before merging.

## Contributing to the code

Improvements to the automation, the search site, or the docs are welcome too.
Those are normal pull requests. The cheat-table checks only run on changes under
`tables/`, so a code change goes straight to human review with no table validation.

Please keep code changes and table submissions in separate pull requests, so the
table automation and the code review stay out of each other's way.
