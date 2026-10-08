# LEMMA.DISCOUNT_FACTOR

Factor that converts an amount at the end of a number of periods into its value today: 1 / (1 + rate) ^ periods.

```
=LEMMA.DISCOUNT_FACTOR(rate, periods)
```

## Definition

1 / (1 + rate) ^ periods, per [Wikipedia, Discounting](https://en.wikipedia.org/wiki/Discounting).

## Example

`=LEMMA.DISCOUNT_FACTOR(0.1, 1)` returns 0.909091 (one period at 10 percent).

## When not to use it

- Continuous discounting, which uses EXP(-rate * periods).
- A series of cash flows. Use LEMMA.NPV.
