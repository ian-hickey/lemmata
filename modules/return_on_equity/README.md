# LEMMA.RETURN_ON_EQUITY

Return on equity: net_income / average_equity for the period, returned as a decimal rate.

```
=LEMMA.RETURN_ON_EQUITY(net_income, average_equity)
```

## Definition

net_income / average_equity, per [Wikipedia, Return on equity](https://en.wikipedia.org/wiki/Return_on_equity).

## Example

`=LEMMA.RETURN_ON_EQUITY(150000, 1000000)` returns 0.15 (15 percent return).

## When not to use it

- Companies with negative equity.
- Comparing firms that define equity differently (average versus opening).
