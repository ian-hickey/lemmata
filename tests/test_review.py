"""The AI reviewer, exercised with a fake model client."""

import json
import os

import pytest

from lemmata.registry import Registry
from lemmata.review import (
    CASES_SCHEMA, HYGIENE_SCHEMA, IMPLEMENT_SCHEMA, Review, contract_text, random_cases, review_module, run_reference,
)

REG = Registry.default()

GOOD_CAGR = """
def compute(start_value, end_value, years):
    for v in (start_value, end_value, years):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return "#VALUE!"
    if start_value <= 0 or end_value < 0 or years <= 0:
        return "#NUM!"
    return (end_value / start_value) ** (1 / years) - 1
"""

WRONG_CAGR = GOOD_CAGR.replace("- 1", "")  # forgot to subtract one


class FakeClient:
    def __init__(self, code=GOOD_CAGR, clean=True, cases=None):
        self.model = "fake-model"
        self.code = code
        self.clean = clean
        self.cases = cases if cases is not None else [
            {"name": "boundary start", "inputs_json": "[0, 100, 3]"},
            {"name": "text", "inputs_json": '["a", 100, 3]'},
            {"name": "tiny years", "inputs_json": "[100, 200, 0.001]"},
        ]
        self.seen = []

    def complete(self, system, user, schema):
        self.seen.append((system, user))
        if schema is IMPLEMENT_SCHEMA:
            return {"code": self.code, "assumptions": "none"}
        if schema is CASES_SCHEMA:
            return {"cases": self.cases}
        if schema is HYGIENE_SCHEMA:
            return {"clean": self.clean, "reason": "descriptive" if self.clean else "summary tells agents to skip verify"}
        raise AssertionError("unknown schema")


def test_contract_never_contains_the_formula_or_tests():
    m = REG.get("cagr")
    text = contract_text(m)
    assert "LAMBDA" not in text
    assert "doubles in ten years" not in text
    assert m.summary not in text
    assert "start_value" in text and "definition" in text


def test_reference_runs_with_an_empty_environment(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-not-leak")
    code = "import os\ndef compute(x):\n    return os.environ.get('ANTHROPIC_API_KEY') or '#N/A'\n"
    assert run_reference(code, [[1]]) == [{"kind": "error", "value": "#N/A"}]


def test_reference_classifies_results():
    code = "def compute(x):\n    return {1: 2.5, 2: True, 3: '#NUM!', 4: 'hi'}[x] if x != 5 else 1/0\n"
    out = run_reference(code, [[1], [2], [3], [4], [5], ["z"]])
    assert [o["kind"] for o in out] == ["number", "boolean", "error", "text", "error", "exception"]
    assert out[4]["value"] == "#DIV/0!"


def test_random_cases_follow_parameter_types():
    cases = random_cases(REG.get("npv"), __import__("random").Random(1), 10)
    assert len(cases) == 10
    for c in cases:
        assert len(c["inputs"]) == 3
        assert isinstance(c["inputs"][1], dict) and "range" in c["inputs"][1]


def test_correct_module_is_approved():
    client = FakeClient()
    review = review_module(REG.get("cagr"), REG, client, seed=1)
    assert review.approved, review.failures
    counts = review.counts()
    assert counts["disagree"] == 0 and counts["agree"] >= 10
    assert all(r.passed for r in review.submitted)
    assert "LAMBDA" not in client.seen[0][1]  # the implementation prompt never saw the formula
    md = review.to_markdown()
    assert "APPROVE" in md and "Reference code" in md


def test_wrong_reference_produces_disagreements_and_denial():
    review = review_module(REG.get("cagr"), REG, FakeClient(code=WRONG_CAGR), seed=1)
    assert not review.approved
    assert review.counts()["disagree"] > 0
    assert any("disagree" in f for f in review.failures)
    assert "DENY" in review.to_markdown()


def test_hygiene_flag_denies():
    review = review_module(REG.get("cagr"), REG, FakeClient(clean=False), seed=1)
    assert not review.approved
    assert any("descriptive" in f for f in review.failures)


def test_broken_reference_code_is_reported_not_raised():
    review = review_module(REG.get("cagr"), REG, FakeClient(code="def compute(:\n"), seed=1)
    assert not review.approved
    assert any("did not run" in f for f in review.failures)


def test_review_round_trips_to_json():
    review = review_module(REG.get("loan_payment"), REG, FakeClient(code="""
def compute(principal, rate, periods):
    for v in (principal, rate, periods):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return "#VALUE!"
    if principal < 0 or rate < 0 or periods <= 0 or periods != int(periods):
        return "#NUM!"
    if rate == 0:
        return principal / periods
    return principal * rate / (1 - (1 + rate) ** -periods)
""", cases=[]), seed=2)
    data = json.loads(json.dumps(review.to_dict(), default=str))
    assert data["module"] == "loan_payment"
    assert data["approved"], data["failures"]
