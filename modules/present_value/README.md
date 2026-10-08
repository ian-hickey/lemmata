# LEMMA.PRESENT_VALUE

Present value of a single amount received after a number of periods at a constant rate per period: future_value / (1 + rate) ^ periods.

```
=LEMMA.PRESENT_VALUE(future_value, rate, periods)
```

## Definition

future_value / (1 + rate) ^ periods, per [Wikipedia, Present value](https://en.wikipedia.org/wiki/Present_value).

## Example

`=LEMMA.PRESENT_VALUE(1000, 0.05, 10)` returns 613.913 (1,000 in ten years at 5 percent).

## When not to use it

- A series of payments. Use LEMMA.ANNUITY_PV for level payments or LEMMA.NPV for an arbitrary series.
- Continuous compounding. This module compounds once per period.
