#!/usr/bin/env sh
# One-time GitHub setup. Run from the repo root after `gh auth login`.
#   scripts/setup_github.sh [owner/name]
# Branch protection (which checks must pass before a merge) is left to you to
# configure in the repository settings.
set -eu
REPO="${1:-ian-hickey/lemmata}"

gh repo create "$REPO" --public --source=. --remote=origin --push \
  --description "Reviewed, tested, hash-pinned spreadsheet formulas for AI agents"

echo "Paste the Anthropic API key the reviewer will use:"
gh secret set ANTHROPIC_API_KEY --repo "$REPO"
gh variable set LEMMATA_REVIEW_MODEL --repo "$REPO" --body "claude-opus-5-5"

# Pages served from the publish workflow.
gh api -X POST "repos/$REPO/pages" -f build_type=workflow >/dev/null 2>&1 || echo "Pages already enabled"

echo "Done. The registry publishes to https://$(echo "$REPO" | cut -d/ -f1).github.io/$(echo "$REPO" | cut -d/ -f2)/ after the first push to main."
