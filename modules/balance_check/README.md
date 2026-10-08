# LEMMA.BALANCE_CHECK

TRUE when assets equal liabilities plus equity within a tolerance, FALSE otherwise: ABS(assets - (liabilities + equity)) <= tolerance.

```
=LEMMA.BALANCE_CHECK(assets, liabilities, equity, tolerance)
```

## Definition

ABS(assets - (liabilities + equity)) <= tolerance, per [Wikipedia, Accounting equation](https://en.wikipedia.org/wiki/Accounting_equation).

## Example

`=LEMMA.BALANCE_CHECK(1000, 600, 400, 0)` returns True (balances exactly).

## When not to use it

- Checking individual accounts, only the totals.
- Statements in different currencies.
