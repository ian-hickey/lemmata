#!/usr/bin/env sh
# One-time GitHub setup. Run from the repo root after `gh auth login`.
#   scripts/setup_github.sh [owner/name]
set -eu
REPO="${1:-ian-hickey/lemmata}"

if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --source=. --remote=origin --push \
    --description "Reviewed, tested, hash-pinned spreadsheet formulas for AI agents"
fi

echo "Paste the Anthropic API key the reviewer will use:"
gh secret set ANTHROPIC_API_KEY --repo "$REPO"
gh variable set LEMMATA_REVIEW_MODEL --repo "$REPO" --body "claude-opus-5-5"

# Pages served from the publish workflow.
gh api -X POST "repos/$REPO/pages" -f build_type=workflow >/dev/null 2>&1 || echo "Pages already enabled"

# Merges wait for the test and review checks; no human approval is required,
# because the review check is the gate. Auto-merge lets an approved pull
# request land on its own.
gh repo edit "$REPO" --enable-auto-merge --delete-branch-on-merge
gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<'JSON' >/dev/null
{
  "required_status_checks": {"strict": true, "contexts": ["test", "review"]},
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
JSON
echo "Done. The registry publishes to https://$(echo "$REPO" | cut -d/ -f1).github.io/$(echo "$REPO" | cut -d/ -f2)/ on every push to main."
