"""Run module tests on real Excel for Mac through AppleScript.

One workbook holds every case: inputs on a Data sheet, one formula cell per
case on a Tests sheet beside a helper cell that renders the result as a typed
string, and every module injected as a defined name. Excel opens the file,
recalculates, and hands the helper column back; nothing is written by Excel,
so its sandbox never asks for permission. The workbook lives in Excel's own
container directory, which it may read without a prompt.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import openpyxl

from .module import Module
from .registry import Registry
from .runner import DEFAULT_TOLERANCE, CaseResult, _rows, literal, matches
from .xlsx import inject

ENGINE = "excel"
CONTAINER = Path.home() / "Library" / "Containers" / "com.microsoft.Excel" / "Data" / "lemmata"
ERROR_CODES = {1: "#NULL!", 2: "#DIV/0!", 3: "#VALUE!", 4: "#REF!", 5: "#NAME?", 6: "#NUM!", 7: "#N/A", 8: "#GETTING_DATA", 14: "#SPILL!"}
HELPER = ('=IF(ISERROR({c}),"ERR:"&ERROR.TYPE({c}),IF(ISNUMBER({c}),"NUM:"&TEXT({c},"0.00000000000000E+00"),'
          'IF(ISLOGICAL({c}),IF({c},"BOOL:TRUE","BOOL:FALSE"),"TEXT:"&{c})))')
APPLESCRIPT = """
tell application "Microsoft Excel"
  open workbook workbook file name ((POSIX file "{path}") as text)
  calculate
  set vals to value of range "D2:D{last}" of worksheet "Tests" of workbook "{name}"
  close workbook "{name}" saving no
end tell
set AppleScript's text item delimiters to linefeed
return vals as text
"""


def excel_available() -> bool:
    return Path("/Applications/Microsoft Excel.app").exists()


def build_workbook(path: Path, registry: Registry, modules: list[Module]) -> list[tuple[Module, dict]]:
    """Write the test workbook. Returns (module, case) per row from row 2 downwards."""
    wb = openpyxl.Workbook()
    tests = wb.active
    tests.title = "Tests"
    data = wb.create_sheet("Data")
    tests.append(["module", "case", "result", "typed"])
    plan = []
    next_col = 1
    for m in modules:
        for i, case in enumerate(m.cases):
            args = []
            for value in case.get("inputs") or []:
                if isinstance(value, dict) and "range" in value:
                    rows = _rows(value["range"])
                    height, width = len(rows), max((len(r) for r in rows), default=1)
                    for r, row in enumerate(rows, start=1):
                        for c, cell in enumerate(row, start=next_col):
                            if cell is not None:
                                data.cell(row=r, column=c, value=cell)
                    first = openpyxl.utils.get_column_letter(next_col)
                    last = openpyxl.utils.get_column_letter(next_col + width - 1)
                    args.append(f"Data!${first}$1:${last}${height}")
                    next_col += width + 1
                else:
                    args.append(literal(value))
            row = tests.max_row + 1
            tests.cell(row=row, column=1, value=m.id)
            tests.cell(row=row, column=2, value=str(case.get("name") or f"case {i}"))
            tests.cell(row=row, column=3, value=f"={m.name}({','.join(args)})")
            tests.cell(row=row, column=4, value=HELPER.format(c=f"C{row}"))
            plan.append((m, case))
    wb.calculation.fullCalcOnLoad = True
    wb.save(path)
    inject(path, registry.with_dependencies(modules))
    return plan


def read_in_excel(path: Path, rows: int, timeout: float = 600) -> list[str]:
    script = APPLESCRIPT.format(path=path, name=path.name, last=rows + 1)
    proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"Excel automation failed: {proc.stderr.strip()[-500:]}")
    lines = proc.stdout.rstrip("\n").split("\n")
    if len(lines) != rows:
        raise RuntimeError(f"expected {rows} results from Excel, got {len(lines)}")
    return lines


def parse_typed(text: str) -> tuple[object, str]:
    if text.startswith("NUM:"):
        return float(text[4:]), "number"
    if text.startswith("ERR:"):
        return ERROR_CODES.get(int(float(text[4:])), text), "error"
    if text.startswith("BOOL:"):
        return text == "BOOL:TRUE", "boolean"
    if text.startswith("TEXT:"):
        return text[5:], "text"
    return text, "unknown"


def run_all_excel(registry: Registry, ids: list[str] | None = None, keep: Path | None = None) -> list[CaseResult]:
    if not excel_available():
        raise RuntimeError("Microsoft Excel is not installed at /Applications/Microsoft Excel.app")
    modules = [registry.get(i) for i in ids] if ids else registry.modules
    CONTAINER.mkdir(parents=True, exist_ok=True)
    path = CONTAINER / f"tests-{os.getpid()}-{int(time.time())}.xlsx"
    plan = build_workbook(path, registry, modules)
    try:
        lines = read_in_excel(path, len(plan))
    finally:
        if keep:
            keep.parent.mkdir(parents=True, exist_ok=True)
            path.replace(keep)
        elif path.exists():
            path.unlink()
    results = []
    for (m, case), text in zip(plan, lines):
        value, kind = parse_typed(text)
        ok, message = matches(case.get("expect"), value, kind, float(case.get("tolerance", DEFAULT_TOLERANCE)))
        results.append(CaseResult(m.id, str(case.get("name") or ""), list(case.get("inputs") or []), case.get("expect"), value, ok, ENGINE, message))
    return results
