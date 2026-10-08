"""The Excel for Mac engine. Live tests run only where Excel is installed."""

import pytest

from lemmata.excel_mac import ERROR_CODES, excel_available, parse_typed, run_all_excel
from lemmata.registry import Registry

REG = Registry.default()


def test_parse_typed_covers_every_kind():
    assert parse_typed("NUM:7.17734625362931E-02") == (pytest.approx(0.0717734625362931), "number")
    assert parse_typed("ERR:6") == ("#NUM!", "error")
    assert parse_typed("ERR:3") == ("#VALUE!", "error")
    assert parse_typed("BOOL:TRUE") == (True, "boolean")
    assert parse_typed("BOOL:FALSE") == (False, "boolean")
    assert parse_typed("TEXT:hi, there") == ("hi, there", "text")
    assert set(ERROR_CODES.values()) >= {"#VALUE!", "#NUM!", "#DIV/0!", "#N/A"}


@pytest.mark.skipif(not excel_available(), reason="Microsoft Excel is not installed")
def test_modules_pass_on_excel():
    results = run_all_excel(REG, ["cagr", "npv", "sum_check", "fiscal_quarter"])
    failures = [f"{r.module_id}/{r.case}: {r.message}" for r in results if not r.passed]
    assert not failures, "\n".join(failures)
    assert len(results) >= 40


@pytest.mark.skipif(not excel_available(), reason="Microsoft Excel is not installed")
def test_excel_engine_detects_a_wrong_expectation():
    import copy

    m = copy.copy(REG.get("cagr"))
    m.tests = {"cases": [{"name": "deliberately wrong", "inputs": [100, 200, 10], "expect": 0.5}, {"name": "right", "inputs": [100, 200, 10], "expect": 0.07177346253629313}]}

    class One:
        modules = [m]
        prefix = REG.prefix

        def get(self, key):
            return m

        def with_dependencies(self, mods):
            return REG.with_dependencies(mods)

    results = run_all_excel(One(), ["cagr"])
    assert [r.passed for r in results] == [False, True]
    assert results[0].actual == pytest.approx(0.0717734625362931)
