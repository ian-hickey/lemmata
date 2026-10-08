from af import canonical
from af.canonical import canonical_formula, formula_hash, lambda_parameters, function_calls


def test_whitespace_and_case_do_not_change_identity():
    a = "=LAMBDA(x, y,\n  if(x > y, x, y))"
    b = "lambda(x,y,IF(x>y,x,y))"
    assert canonical_formula(a) == canonical_formula(b) == "LAMBDA(X,Y,IF(X>Y,X,Y))"
    assert formula_hash(a) == formula_hash(b)


def test_string_literals_are_preserved():
    f = 'LAMBDA(x, IF(x = "Hello  World", "a""b", x))'
    assert canonical_formula(f) == 'LAMBDA(X,IF(X="Hello  World","a""b",X))'


def test_lambda_parameters_and_calls():
    f = "LAMBDA(rate, cashflows, LET(n, ROWS(cashflows), SUMPRODUCT(cashflows / (1 + rate) ^ SEQUENCE(n))))"
    assert lambda_parameters(f) == ["rate", "cashflows"]
    assert function_calls(f) == {"LAMBDA", "LET", "ROWS", "SUMPRODUCT", "SEQUENCE"}


def test_split_args_handles_nesting_and_strings():
    masked = canonical.mask_strings('F(a, G(b, "c,d"), e)')
    spans = canonical.split_args(masked, 1)
    assert len(spans) == 3
