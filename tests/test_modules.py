import pytest

from af.registry import Registry
from af.runner import IronCalcEngine, run_module

REG = Registry.default()
ENGINE = IronCalcEngine()


def test_registry_has_phase0_modules():
    assert {m.id for m in REG.modules} >= {"cagr", "loan_payment", "npv"}


@pytest.mark.parametrize("module", REG.modules, ids=lambda m: m.id)
def test_module_conforms_to_spec(module):
    assert module.validate(REG.prefix) == []


@pytest.mark.parametrize("module", REG.modules, ids=lambda m: m.id)
def test_module_cases_pass_on_ironcalc(module):
    results = run_module(module, REG, ENGINE)
    failures = [f"{r.case}: {r.message}" for r in results if not r.passed]
    assert not failures, "\n".join(failures)


def test_hashes_are_distinct_and_stable():
    hashes = {m.module_hash for m in REG.modules}
    assert len(hashes) == len(REG.modules)
    for m in REG.modules:
        assert m.formula_hash != m.module_hash
