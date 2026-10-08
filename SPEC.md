# Module specification v0.1 (draft)

A module is a reviewed spreadsheet formula with a contract, tests, and a content hash. This document defines the folder format, the canonical form, the hashing rule, and how a module is written into an `.xlsx` file.

## Folder layout

One folder per module under `modules/`, named by the module id.

| File | Holds |
| --- | --- |
| `module.yaml` | Name, version, summary, parameters with types and units, conventions, tags, dependencies, license |
| `formula.lambda` | The LAMBDA in plain Excel syntax, readable in a diff |
| `tests.yaml` | Inputs and expected outputs, edge cases, expected errors, and the source each reference case comes from |
| `README.md` | What it calculates, the definition it follows, when not to use it |

## module.yaml

```yaml
id: cagr                      # ^[a-z][a-z0-9_]*$, equals the folder name
name: AF.CAGR                 # the defined name in the workbook; prefix + upper case
version: 0.1.0                # semver
summary: One line, 240 characters or fewer. Agents choose by this text.
definition:
  source: Where the definition comes from
  url: https://...
  formula: the definition in plain notation
parameters:                   # same names and order as the LAMBDA's parameters
  - name: start_value
    type: number              # number | text | boolean | range | any
    unit: currency
    description: ...
returns:
  type: number
  unit: decimal rate per year
  description: ...
errors:
  "#VALUE!": when it is returned
  "#NUM!": when it is returned
conventions: [...]            # sign conventions, timing, what is not handled
tags: [...]
dependencies: []              # [{id, module_hash}] of other modules this one calls
license: MIT-0
```

## formula.lambda

The file holds exactly one `LAMBDA(...)` expression. Whitespace and newlines are free. Parameter names match `^[a-z_][a-z0-9_]*$` and must not look like cell references.

Rules:

- The formula validates its arguments before calculating and returns a standard Excel error on bad input: `#VALUE!` for a wrong type, `#NUM!` for a value outside the allowed domain.
- The formula is pure. It must return the same output for the same input. Banned: `WEBSERVICE`, `RTD`, `NOW`, `TODAY`, `RAND`, `RANDBETWEEN`, `RANDARRAY`, `INDIRECT`, `OFFSET`, `CELL`, `INFO`, `HYPERLINK`, `FILTERXML`, `ENCODEURL`, `IMAGE`, `STOCKHISTORY`, and every `CUBE*` function.
- The formula references no cells, sheets, external workbooks, or structured references. Everything it needs arrives through its parameters.
- Other modules may be called by name, and each one is listed under `dependencies` with its hash.

## Canonical form

Identity must not change when someone reformats a formula. The canonical form of a formula is:

1. A leading `=` is removed.
2. Outside string literals, all whitespace is removed and all characters are upper-cased.
3. String literals are kept byte for byte.

The canonical form of `module.yaml` is its content as JSON with sorted keys and no whitespace (`json.dumps(meta, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`).

## Hashes

Two hashes are defined, because a workbook holds only the formula text.

| Hash | Over | Used for |
| --- | --- | --- |
| `formula_hash` | SHA-256 of the canonical formula | What a verifier can recompute from a workbook alone |
| `module_hash` | SHA-256 of canonical formula, a newline, and canonical `module.yaml` | The module's identity, what the version label and attestations refer to |

Test results are attached to a `module_hash` and are not part of it, so adding tests later does not create a new version. Any change to the formula or to `module.yaml` is a new version with a new hash.

## Inside the workbook

A module becomes a workbook-scoped defined name. In the file the formula is stored as Excel requires: `_xlfn.` before each function introduced after Excel 2007 (including `LAMBDA` and `LET`), and `_xlpm.` before each LAMBDA parameter and LET variable. The `af` library does this translation; writing the name by hand usually gets it wrong and opens as `#NAME?`.

The defined name's comment records the label:

```
<id>@<version> sha256:<module_hash>
```

A verifier does not trust the label. It strips the file prefixes, canonicalizes the formula, computes `formula_hash`, and looks that up in the registry. The label must then agree with the module found. Statuses:

| Status | Meaning |
| --- | --- |
| `current` | Formula matches a registry module and the label agrees |
| `unlabeled` | Formula matches a registry module but has no label |
| `label_mismatch` | Formula matches one module, the label names another |
| `modified` | Label names a known module but the formula no longer matches it |
| `unknown` | Neither the formula nor the label is known to the registry |
| `advisory` | Formula matches a module that has an open advisory |

## Labels

| Label | Means |
| --- | --- |
| Tested | Passes its own tests in CI |
| AI-reviewed | Also matched the reviewer's independent implementation on generated cases |
| Human-verified | A named person with domain knowledge also checked it |

AI-reviewed is the bar for publishing. Nothing in the repo carries that label yet.

## tests.yaml

```yaml
cases:
  - name: doubles in ten years
    inputs: [100, 200, 10]            # scalars are passed as literals
    expect: 0.07177346253629313       # a number, text, boolean, or an error such as "#NUM!"
    tolerance: 1.0e-9                 # optional, absolute and relative; default 1e-9
    source: computed from the definition
  - name: a range argument
    inputs: [0.1, {range: [[-100], [30], [40], [50]]}, 0]
    expect: -2.1036814425244366
```

A `range` value is a list of rows. A flat list is one column. `null` leaves a cell blank. The runner writes the range into a sheet and passes a reference to it.

## Open points

- Function prefix. `AF.` is a placeholder until the project is named.
- Version history. Older hashes will live in the published `index.json`, so a verifier can report `outdated`. The repo holds only the current version of each module.
- A companion `.CHECK` function that returns a text reason for an error is planned but not yet specified.
