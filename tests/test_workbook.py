"""Inject modules into a workbook, read it back through IronCalc, and verify it."""

import openpyxl
import ironcalc
import pytest
from openpyxl.workbook.defined_name import DefinedName

from af.registry import Registry
from af.verify import verify_workbook
from af.xlsx import inject

REG = Registry.default()


@pytest.fixture
def workbook(tmp_path):
    path = tmp_path / "model.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Model"
    ws["A1"], ws["A2"], ws["A3"] = 100, 200, 10
    ws["B1"] = "=AF.CAGR(A1, A2, A3)"
    ws["B2"] = "=AF.LOAN_PAYMENT(200000, 0.05/12, 360)"
    for i, v in enumerate([-100, 30, 40, 50], start=1):
        ws.cell(row=i, column=4, value=v)
    ws["B3"] = "=AF.NPV(0.1, D1:D4, 0)"
    wb.save(path)
    inject(path, REG.with_dependencies([REG.get("cagr"), REG.get("loan_payment"), REG.get("npv")]))
    return path


def test_ironcalc_evaluates_injected_modules(workbook):
    m = ironcalc.load_from_xlsx(str(workbook), "en", "UTC")
    m.evaluate()
    assert m.get_cell_value(0, 1, 2) == pytest.approx(0.07177346253629313)
    assert m.get_cell_value(0, 2, 2) == pytest.approx(1073.6432460242797)
    assert m.get_cell_value(0, 3, 2) == pytest.approx(-2.1036814425244366)


def test_verify_reports_current(workbook):
    report = verify_workbook(workbook, REG)
    assert report["ok"]
    assert {e["name"] for e in report["names"]} == {"AF.CAGR", "AF.LOAN_PAYMENT", "AF.NPV"}
    assert all(e["status"] == "current" for e in report["names"])


def test_verify_flags_hand_edited_formula(workbook):
    wb = openpyxl.load_workbook(workbook)
    dn = wb.defined_names["AF.CAGR"]
    wb.defined_names["AF.CAGR"] = DefinedName("AF.CAGR", attr_text=dn.attr_text.replace("- 1", "- 2"), comment=dn.comment)
    wb.save(workbook)
    report = verify_workbook(workbook, REG)
    assert not report["ok"]
    assert {e["name"]: e["status"] for e in report["names"]}["AF.CAGR"] == "modified"


def test_verify_flags_missing_and_wrong_labels(workbook):
    wb = openpyxl.load_workbook(workbook)
    npv = wb.defined_names["AF.NPV"]
    wb.defined_names["AF.NPV"] = DefinedName("AF.NPV", attr_text=npv.attr_text, comment=None)
    cagr = wb.defined_names["AF.CAGR"]
    wb.defined_names["AF.CAGR"] = DefinedName("AF.CAGR", attr_text=cagr.attr_text, comment=REG.get("npv").label)
    wb.save(workbook)
    statuses = {e["name"]: e["status"] for e in verify_workbook(workbook, REG)["names"]}
    assert statuses["AF.NPV"] == "unlabeled"
    assert statuses["AF.CAGR"] == "label_mismatch"
    assert statuses["AF.LOAN_PAYMENT"] == "current"


def test_verify_flags_advisory(workbook, tmp_path, monkeypatch):
    reg = Registry(REG.root)
    mod = reg.get("npv")
    advisories_dir = tmp_path / "advisories"
    advisories_dir.mkdir()
    (advisories_dir / "2026-001.yaml").write_text(
        f"module_id: npv\nmodule_hash: {mod.module_hash}\nseverity: high\nsummary: test advisory\nfixed_version: null\n"
    )
    reg.advisories_dir = advisories_dir
    statuses = {e["name"]: e["status"] for e in verify_workbook(workbook, reg)["names"]}
    assert statuses["AF.NPV"] == "advisory"
