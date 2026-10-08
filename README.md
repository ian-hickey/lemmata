# Lemmata

Reviewed, tested, hash-pinned spreadsheet formulas. Built for AI agents, usable by anyone.

A lemma is a small result that is proven once and then cited by everything built on it. Each module here is one: a formula with a cited definition, a test suite, and a content hash, so an agent writes `=LEMMA.NPV(...)` instead of deriving net present value again and hoping. The registry is the lemmata.

## Why

Spreadsheet errors cost real money, and most start with a formula someone wrote from scratch and nobody checked. AI agents now write spreadsheets at scale and repeat the same mistakes faster. This project gives them a known-good building block to reach for instead.

## What a module is

- An Excel LAMBDA with input checks built in
- A test suite tied to a cited definition
- A content hash, so a workbook can prove which version it runs

Each module is one folder under [modules/](modules/) with four files: `module.yaml`, `formula.lambda`, `tests.yaml`, and `README.md`. The format is specified in [SPEC.md](SPEC.md).

## How agents use it

1. Search the registry for a calculation.
2. Insert the module into the workbook.
3. Run verify before returning the file.

Four ways in, all reading the same published registry:

| Path | Use |
| --- | --- |
| MCP server | `uvx --from git+https://github.com/ian-hickey/lemmata lemma mcp` gives any MCP client four tools: `search_modules`, `get_module`, `insert_modules`, `verify_workbook` |
| Python | `from lemmata.registry import Registry` then `Registry.default()`, `lemmata.xlsx.inject`, `lemmata.verify.verify_workbook` |
| JavaScript | the [`lemmata`](js/) package: `injectModules`, `createWorkbook`, `verifyWorkbook` against `index.json` |
| HTTP only | `https://ian-hickey.github.io/lemmata/index.json` and `llms.txt`; each entry carries the formula in source and file form |

MCP client configuration:

```json
{"mcpServers": {"lemmata": {"command": "uvx", "args": ["--from", "git+https://github.com/ian-hickey/lemmata", "lemma", "mcp"]}}}
```

Two lines for an agent's instructions: check Lemmata before writing a financial formula, and run `verify_workbook` before returning a file. See [AGENTS.md](AGENTS.md).

The registry is resolved from `LEMMATA_REGISTRY` (a checkout path or a URL), else this checkout, else the public site. Downloads are cached and re-hashed; a module whose files do not hash to the index entry is rejected.

## Quick start

```sh
uv sync
uv run lemma list                          # modules in the registry
uv run lemma test                          # run every module's tests on IronCalc
uv run lemma add model.xlsx cagr npv       # inject modules into a workbook (creates it if missing)
uv run lemma verify model.xlsx             # re-hash every LEMMA.* name and report status
```

A cell can then call a module like any function: `=LEMMA.CAGR(100, 200, 10)`.

## Principles

- A published module is never edited. A fix is a new version.
- Bad input returns an error, never a number.
- Everything is served as static files. No account, no server, no blockchain.
- Labels say exactly what review a module has had.

## How a module gets in

Every pull request is tested on IronCalc and reviewed by an AI reviewer that writes its own implementation from the cited definition, compares the two on generated cases, and posts the evidence. A failed comparison fails the check. On merge, the registry is rebuilt, each module tarball is attested with Sigstore, and the result is deployed to GitHub Pages as `index.json`, `llms.txt`, and one folder per module hash. See [CONTRIBUTING.md](CONTRIBUTING.md).

```sh
uv run lemma review cagr               # run the reviewer locally (needs ANTHROPIC_API_KEY)
gh attestation verify modules/<hash>.tar.gz -R ian-hickey/lemmata   # check a published module
```

## Status

Phase 3. Forty modules are published across time value of money, loans and amortization, depreciation, growth and returns, margins and ratios, fiscal periods and day counts, and reconciliation checks. Each one cites its definition, carries at least ten computed test cases, and passed the AI reviewer, whose report is kept in [reviews/](reviews/) under the module's hash. The MCP server, CLI, Python and JavaScript injectors, and verifier are built.

Excel conformance is still checked by hand: run `uv run python scripts/phase0_demo.py` and open `examples/phase0.xlsx`.

## Known engine differences

The test suite runs on IronCalc 0.8.3. Excel is the reference engine. Differences found so far:

- `ISNUMBER(range)` is not lifted over arrays in IronCalc, so modules validate ranges with `COUNT(range) = ROWS(range) * COLUMNS(range)` instead.
- `ROWS(scalar)` returns an error in IronCalc where Excel returns 1. Range parameters must be given a range, not a single number.
- A one-cell range passed where a LAMBDA expects a number is treated as its value by Excel but fails `ISNUMBER` in IronCalc. The reviewer's case generator therefore unwraps one-cell ranges for scalar parameters.
- IronCalc returns `#NUM!` for magnitudes around 1e-300 or 1e300 that Excel handles. The reviewer verifies inputs between 1e-9 and 1e12 only.
- Date serials below 61 (before 1 March 1900) differ between engines because of Excel's 1900 leap-year quirk. Modules reject them.
- Exact comparisons that turn on binary rounding, such as 0.1 + 0.2 against 0.3, differ between IronCalc and a Python reference. The reviewer's case generator avoids them.

## License

Tools are Apache-2.0 ([LICENSE](LICENSE)). Modules are MIT-0 ([modules/LICENSE](modules/LICENSE)), so a formula can sit in any workbook without a notice.
