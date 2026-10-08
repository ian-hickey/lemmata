"""The Lemmata MCP server: search, fetch, insert, and verify from any MCP client.

Run it with `lemma mcp` (stdio). The registry comes from LEMMATA_REGISTRY (a
checkout path or a URL), else this checkout, else the public site.
"""

from __future__ import annotations

import re
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from .module import Module
from .registry import Registry
from .verify import verify_workbook as _verify
from .xlsx import inject, to_file_formula

INSTRUCTIONS = """Lemmata is a registry of reviewed, tested, hash-pinned spreadsheet formulas (Excel LAMBDAs).
Before writing a financial or business calculation into a workbook, search here for a module.
Insert modules with insert_modules, which writes them correctly into the .xlsx file, then call
the module in cells like any function, for example =LEMMA.CAGR(A1, A2, A3). Run verify_workbook
before returning a file; every LEMMA.* name must report status current."""

WORD_RE = re.compile(r"[a-z0-9]+")


def _summary(m: Module) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "version": m.version,
        "summary": m.summary,
        "signature": f"{m.name}({', '.join(p['name'] for p in m.parameters)})",
        "parameters": m.parameters,
        "returns": m.meta.get("returns"),
        "tags": m.meta.get("tags") or [],
        "module_hash": m.module_hash,
    }


def score(module: Module, terms: list[str]) -> tuple[int, int]:
    """(distinct query terms matched, weighted hits): a module matching every term outranks a heavier partial match."""
    haystacks = [
        (module.id.replace("_", " "), 6),
        (module.name.lower().replace("_", " ").replace(".", " "), 6),
        (" ".join(module.meta.get("tags") or []), 4),
        (module.summary.lower(), 3),
        (" ".join(str(p.get("name", "")).replace("_", " ") for p in module.parameters), 2),
        (module.readme.lower(), 1),
    ]
    total = 0
    matched = 0
    for term in terms:
        hit = False
        for text, weight in haystacks:
            if term in text:
                total += weight
                hit = True
        matched += hit
    if terms and " ".join(terms) in module.summary.lower():
        total += 10
    return matched, total


def build_server(registry: Registry | None = None) -> MCPServer:
    reg = registry or Registry.default()
    server = MCPServer("lemmata", instructions=INSTRUCTIONS, version="0.0.1")

    @server.tool(description="Search the registry for a calculation. Returns modules ranked by how well their name, tags, summary, and parameters match the query.")
    def search_modules(query: str, limit: int = 10) -> list[dict]:
        terms = WORD_RE.findall(query.lower())
        ranked = sorted(((score(m, terms), m) for m in reg.modules), key=lambda x: (-x[0][0], -x[0][1], x[1].id))
        hits = [m for s, m in ranked if s[0] > 0] if terms else list(reg.modules)
        return [_summary(m) for m in hits[: max(1, limit)]]

    @server.tool(description="Fetch one module by id, defined name, or hash: its contract, formula, worked examples, hashes, and README.")
    def get_module(module: str) -> dict:
        m = reg.get(module)
        return {
            **_summary(m),
            "definition": m.meta.get("definition"),
            "errors": m.meta.get("errors") or {},
            "conventions": m.meta.get("conventions") or [],
            "formula": m.formula.strip(),
            "formula_xlsx": to_file_formula(m.formula),
            "formula_hash": m.formula_hash,
            "label": m.label,
            "dependencies": m.dependencies,
            "examples": [
                {"inputs": c.get("inputs"), "expect": c.get("expect"), "name": c.get("name")}
                for c in m.cases
            ],
            "readme": m.readme,
        }

    @server.tool(description="Write modules into an .xlsx workbook as defined names, with the file-format prefixes Excel requires. Creates the workbook if the path does not exist. Dependencies are included. Returns the names written and how to call them.")
    def insert_modules(workbook: str, modules: list[str], out: str | None = None) -> dict:
        mods = reg.with_dependencies([reg.get(i) for i in modules])
        written = inject(workbook, mods, out=out)
        return {
            "path": str(Path(out or workbook)),
            "written": written,
            "call_as": [f"={m.name}({', '.join(p['name'] for p in m.parameters)})" for m in mods],
            "next": "Put the formulas in cells, then call verify_workbook before returning the file.",
        }

    @server.tool(description="Re-hash every LEMMA.* defined name in a workbook and check it against the registry. Reports each name's status, every cell that calls it with the ranges it passes, and any LEMMA.* name a cell calls that is not defined.")
    def verify_workbook(workbook: str) -> dict:
        return _verify(workbook, reg)

    return server


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()
