"""A workbook written by the JavaScript injector verifies and evaluates on the Python side."""

import json
import shutil
import subprocess

import pytest

from lemmata.registry import Registry
from lemmata.verify import verify_workbook

REG = Registry.default()
ROOT = REG.root


@pytest.mark.skipif(shutil.which("node") is None or not (ROOT / "js" / "node_modules").exists(), reason="node or js deps missing")
def test_js_written_workbook_verifies_in_python(tmp_path):
    index = tmp_path / "index.json"
    index.write_text(json.dumps({"prefix": "LEMMA.", "modules": [m.to_index_entry() for m in REG.modules], "advisories": []}))
    out = tmp_path / "js.xlsx"
    subprocess.run(["node", str(ROOT / "js" / "scripts" / "demo.mjs"), str(index), str(out), "cagr", "npv"], check=True, capture_output=True)
    report = verify_workbook(out, REG)
    assert report["ok"] and {e["name"] for e in report["names"]} == {"LEMMA.CAGR", "LEMMA.NPV"}

    import ironcalc

    m = ironcalc.load_from_xlsx(str(out), "en", "UTC")
    m.set_user_input(0, 1, 1, "=LEMMA.CAGR(100, 200, 10)")
    m.evaluate()
    assert m.get_cell_value(0, 1, 1) == pytest.approx(0.07177346253629313)
