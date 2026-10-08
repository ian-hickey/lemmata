import pytest

from af.registry import Registry
from af.xlsx import declared_names, from_file_formula, parse_label, to_file_formula


def test_declared_names_cover_lambda_params_and_let_vars():
    f = "LAMBDA(rate, cf, LET(n, ROWS(cf), k, 2, SUMPRODUCT(cf) * n * k))"
    assert declared_names(f) == {"rate", "cf", "n", "k"}


def test_to_file_formula_adds_prefixes():
    f = "LAMBDA(s, e, IF(s > e, #VALUE!, LET(n, 2, SEQUENCE(n) + e)))"
    out = to_file_formula(f)
    assert out == (
        "_xlfn.LAMBDA(_xlpm.s, _xlpm.e, IF(_xlpm.s > _xlpm.e, #VALUE!, "
        "_xlfn.LET(_xlpm.n, 2, _xlfn.SEQUENCE(_xlpm.n) + _xlpm.e)))"
    )


def test_param_named_like_error_word_is_safe():
    f = 'LAMBDA(value, IF(value < 0, #VALUE!, "value"))'
    assert to_file_formula(f) == '_xlfn.LAMBDA(_xlpm.value, IF(_xlpm.value < 0, #VALUE!, "value"))'


def test_prefixing_is_idempotent_and_reversible():
    f = "LAMBDA(x, LET(y, x + 1, SEQUENCE(y)))"
    once = to_file_formula(f)
    assert to_file_formula(once) == once
    assert from_file_formula(once) == f


@pytest.mark.parametrize("module", Registry.default().modules, ids=lambda m: m.id)
def test_every_module_round_trips_through_file_format(module):
    assert from_file_formula(to_file_formula(module.formula)) == module.formula.strip()


def test_parse_label():
    h = "a" * 64
    assert parse_label(f"cagr@0.1.0 sha256:{h}") == {"id": "cagr", "version": "0.1.0", "hash": h}
    assert parse_label("anything else") is None
    assert parse_label(None) is None
