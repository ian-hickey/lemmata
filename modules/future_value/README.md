# LEMMA.FUTURE_VALUE

Future value of a single amount compounded for a number of periods at a constant rate per period: present_value * (1 + rate) ^ periods.

```
=LEMMA.FUTURE_VALUE(present_value, rate, periods)
```

## Definition

present_value * (1 + rate) ^ periods, per [Wikipedia, Future value](https://en.wikipedia.org/wiki/Future_value).

## Example

`=LEMMA.FUTURE_VALUE(1000, 0.05, 10)` returns 1628.89 (1,000 for ten years at 5 percent).

## When not to use it

- Regular contributions. Use LEMMA.ANNUITY_FV.
- A rate that changes over time.
