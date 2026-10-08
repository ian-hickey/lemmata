# Contributing a module

A module is one folder under `modules/` with `module.yaml`, `formula.lambda`, `tests.yaml`, and `README.md`. The format is in [SPEC.md](SPEC.md); copy an existing module to start.

## Before opening a pull request

```sh
uv sync --all-groups
uv run lemma check <id>     # spec rules
uv run lemma test <id>      # your tests on IronCalc
```

Cite the definition the formula implements and include at least one reference case from that source. Compute every expected value; a number typed from memory is the most common test bug.

## What happens on a pull request

1. `ci` runs the spec check, every module's tests on IronCalc, and the tooling tests.
2. `review` runs the AI reviewer with the base branch's tooling and your `modules/` folder. It:
   - runs your tests;
   - writes its own implementation from the cited definition and the parameter contract, without seeing your formula, tests, summary, or README;
   - generates edge cases and random inputs and compares your formula against its implementation;
   - checks the spec rules and whether any text aimed at agents contains instructions;
   - posts a report listing every case it ran, then passes or fails the check.
3. Any failed comparison fails the `review` check. The reviewer cannot pass past it.
4. Within 15 minutes of a merge, `publish` builds the registry, attests each module tarball with Sigstore, and deploys to GitHub Pages.

A pull request whose last commit was pushed by the bot (its review records) needs one more human push, or an update from main, before GitHub counts its checks, unless the repository has a `LEMMATA_BOT_TOKEN` secret for the records push.

Declare the author in the pull request. Where the author is an AI model, the reviewer must run on a different model: a maintainer re-runs the `review` workflow with the `model` input.

## Running the suite on Excel

With Excel for Mac installed, `uv run lemma test --engine excel` runs every case through the real application in about a second. The first run may ask macOS to let your terminal control Excel; allow it. The conformance workflow needs a self-hosted runner on a Mac with Excel: register one from the repository's Actions settings with the label `excel`, run it as a launchd service in a logged-in session, and keep the machine awake.

## Fixing a published module

A published version is never edited. Bump `version`, change the formula, add the failing case to `tests.yaml`, and add an advisory under `advisories/` naming the old hash.
