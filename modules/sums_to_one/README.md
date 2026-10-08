# LEMMA.SUMS_TO_ONE

TRUE when a range of weights or percentages adds up to 1 within a tolerance, FALSE otherwise; every cell must be a number.

```
=LEMMA.SUMS_TO_ONE(weights, tolerance)
```

## Definition

ABS(SUM(weights) - 1) <= tolerance, per [Wikipedia, Weight function, normalized weights](https://en.wikipedia.org/wiki/Weight_function).

## Example

`=LEMMA.SUMS_TO_ONE(range, 0)` returns True (quarters).

## When not to use it

- Weights that are meant to sum to 100. Divide by 100 first.
- Checking that each weight is between 0 and 1, which this does not test.
