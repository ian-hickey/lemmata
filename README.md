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

An MCP server and JavaScript library are planned. The Python library (`lemmata`) and CLI (`lemma`) exist today.

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

## Status

Phase 0. Three modules exist (CAGR, loan payment, NPV with explicit timing), an injector writes them into `.xlsx` files, and their tests run on [IronCalc](https://www.ironcalc.com). Excel conformance is checked by hand for now: run `uv run python scripts/phase0_demo.py` and open `examples/phase0.xlsx`.

Nothing here has been through AI review yet, so no module carries a label above Tested.

## Known engine differences

The test suite runs on IronCalc 0.8.3. Excel is the reference engine. Differences found so far:

- `ISNUMBER(range)` is not lifted over arrays in IronCalc, so modules validate ranges with `COUNT(range) = ROWS(range) * COLUMNS(range)` instead.
- `ROWS(scalar)` returns an error in IronCalc where Excel returns 1. Range parameters must be given a range, not a single number.

## License

Tools are Apache-2.0 ([LICENSE](LICENSE)). Modules are MIT-0 ([modules/LICENSE](modules/LICENSE)), so a formula can sit in any workbook without a notice.
