# Repository Policy

## Commit To Git

- source code
- skill instructions
- schemas
- product facts
- knowledge base
- architecture docs
- small JSON/MD project artifacts

## Do Not Commit To Git

- raw user footage
- final videos
- generated cover images
- extracted frames
- contact sheets
- temporary segment files
- overlay PNG batches
- `.env` files
- API keys

## Why

GitHub should be the control plane for code and repeatable decisions. Media files should live in object storage because they are large, regenerated often, and will later need signed URLs.

## Current Safeguard

The root `.gitignore` excludes common media and generated artifacts. Before pushing, run:

```bash
find . -type f -size +5M | while read f; do git ls-files --error-unmatch "$f" >/dev/null 2>&1 && echo "$f"; done
```

This should print nothing.
