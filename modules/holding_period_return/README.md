# LEMMA.HOLDING_PERIOD_RETURN

Total return over a holding period including income received: (end_value + income - start_value) / start_value, as a decimal.

```
=LEMMA.HOLDING_PERIOD_RETURN(start_value, end_value, income)
```

## Definition

(end_value + income - start_value) / start_value, per [Wikipedia, Holding period return](https://en.wikipedia.org/wiki/Holding_period_return).

## Example

`=LEMMA.HOLDING_PERIOD_RETURN(100, 110, 3)` returns 0.13 (price gain plus dividend).

## When not to use it

- Multiple periods with cash flows in between. Use an IRR-style module.
- Comparing periods of different lengths without annualizing.
