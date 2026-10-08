# LEMMA.DEBT_TO_EQUITY

Debt-to-equity ratio: total_debt / total_equity, a leverage measure.

```
=LEMMA.DEBT_TO_EQUITY(total_debt, total_equity)
```

## Definition

total_debt / total_equity, per [Wikipedia, Debt-to-equity ratio](https://en.wikipedia.org/wiki/Debt-to-equity_ratio).

## Example

`=LEMMA.DEBT_TO_EQUITY(50000, 100000)` returns 0.5 (half as much debt as equity).

## When not to use it

- Companies with negative equity, where the ratio is not meaningful.
- Comparing companies that define debt differently.
