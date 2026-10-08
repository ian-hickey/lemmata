"""Run a module's tests.yaml on a spreadsheet engine. IronCalc is the only engine today."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .module import Module
from .registry import Registry

DEFAULT_TOLERANCE = 1e-9
RANGE_START_COLUMN = 3  # ranges are written from column C rightwards, one blank column apart


@dataclass
class CaseResult:
    module_id: str
    case: str
    inputs: list
    expected: Any
    actual: Any
    passed: bool
    engine: str = "ironcalc"
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "module": self.module_id, "case": self.case, "engine": self.engine,
            "inputs": self.inputs, "expected": self.expected, "actual": self.actual,
            "passed": self.passed, "message": self.message,
        }


def literal(value: Any) -> str:
    """Render a scalar as an Excel formula literal."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return '"' + value.replace('"', '""') + '"'
    raise TypeError(f"cannot render {value!r} as a literal")


def _rows(spec: list) -> list[list]:
    """Normalize a range spec to a list of rows. A flat list is one column."""
    if spec and all(not isinstance(r, list) for r in spec):
        return [[v] for v in spec]
    return [list(r) for r in spec]


class IronCalcEngine:
    name = "ironcalc"

    def __init__(self) -> None:
        import ironcalc

        self.ironcalc = ironcalc

    def evaluate(self, modules: list[Module], target: Module, inputs: list) -> tuple[Any, str]:
        """Return (value, kind) where kind is 'number', 'text', 'boolean', 'error', or 'blank'."""
        ic = self.ironcalc
        m = ic.create("test", "en", "UTC")
        for mod in modules:
            m.new_defined_name(mod.name, None, mod.canonical_formula)
        args: list[str] = []
        next_col = RANGE_START_COLUMN
        for value in inputs:
            if isinstance(value, dict) and "range" in value:
                rows = _rows(value["range"])
                height = len(rows)
                width = max((len(r) for r in rows), default=1)
                for r, row in enumerate(rows, start=1):
                    for c, cell in enumerate(row, start=next_col):
                        if cell is None:
                            continue
                        if isinstance(cell, bool):
                            m.update_cell_with_bool(0, r, c, cell)
                        elif isinstance(cell, (int, float)):
                            m.update_cell_with_number(0, r, c, float(cell))
                        else:
                            m.update_cell_with_text(0, r, c, str(cell))
                first = ic.column_name_from_number(next_col)
                last = ic.column_name_from_number(next_col + width - 1)
                args.append(f"${first}$1:${last}${height}")
                next_col += width + 1
            else:
                args.append(literal(value))
        m.set_user_input(0, 1, 1, f"={target.name}({','.join(args)})")
        m.evaluate()
        value = m.get_cell_value(0, 1, 1)
        kind = str(m.get_cell_type(0, 1, 1)).rsplit(".", 1)[-1]
        mapping = {"Number": "number", "Text": "text", "LogicalValue": "boolean", "ErrorValue": "error"}
        return value, mapping.get(kind, kind.lower())


def matches(expected: Any, actual: Any, kind: str, tolerance: float) -> tuple[bool, str]:
    if isinstance(expected, str) and expected.startswith("#"):
        if kind == "error" and actual == expected:
            return True, ""
        return False, f"expected error {expected}, got {kind} {actual!r}"
    if isinstance(expected, bool):
        if kind == "boolean" and bool(actual) == expected:
            return True, ""
        return False, f"expected {expected}, got {kind} {actual!r}"
    if isinstance(expected, (int, float)):
        if kind != "number":
            return False, f"expected number {expected}, got {kind} {actual!r}"
        diff = abs(float(actual) - float(expected))
        limit = max(tolerance, tolerance * abs(float(expected)))
        if math.isfinite(diff) and diff <= limit:
            return True, ""
        return False, f"expected {expected}, got {actual} (diff {diff:.3g} > {limit:.3g})"
    if isinstance(expected, str):
        if kind == "text" and actual == expected:
            return True, ""
        return False, f"expected text {expected!r}, got {kind} {actual!r}"
    return False, f"unsupported expectation {expected!r}"


def run_module(module: Module, registry: Registry, engine: IronCalcEngine | None = None) -> list[CaseResult]:
    engine = engine or IronCalcEngine()
    modules = registry.with_dependencies([module])
    results = []
    for i, case in enumerate(module.cases):
        name = str(case.get("name") or f"case {i}")
        inputs = list(case.get("inputs") or [])
        expected = case.get("expect")
        tolerance = float(case.get("tolerance", DEFAULT_TOLERANCE))
        try:
            actual, kind = engine.evaluate(modules, module, inputs)
            ok, message = matches(expected, actual, kind, tolerance)
        except Exception as ex:  # engine failure is a failed case, not a crash
            actual, ok, message = None, False, f"engine error: {ex}"
        results.append(CaseResult(module.id, name, inputs, expected, actual, ok, engine.name, message))
    return results


def run_all(registry: Registry, ids: list[str] | None = None) -> list[CaseResult]:
    engine = IronCalcEngine()
    modules = [registry.get(i) for i in ids] if ids else registry.modules
    results: list[CaseResult] = []
    for m in modules:
        results.extend(run_module(m, registry, engine))
    return results
