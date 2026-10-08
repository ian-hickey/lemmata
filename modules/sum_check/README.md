# LEMMA.SUM_CHECK

TRUE when the sum of a range is within a tolerance of an expected total, FALSE otherwise; every cell in the range must be a number.

```
=LEMMA.SUM_CHECK(values, expected_total, tolerance)
```

## Definition

ABS(SUM(values) - expected_total) <= tolerance, per [Wikipedia, Reconciliation (accounting)](https://en.wikipedia.org/wiki/Reconciliation_(accounting)).

## Example

`=LEMMA.SUM_CHECK(range, 60, 0)` returns True (column adds up).

## When not to use it

- Ranges where blanks legitimately mean zero. Fill them with 0 first.
- Matching individual items between two lists.
