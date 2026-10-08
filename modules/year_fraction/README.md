# LEMMA.YEAR_FRACTION

Fraction of a year between two dates under an actual-day count with a 360 or 365 day year: (end_date - start_date) / basis.

```
=LEMMA.YEAR_FRACTION(start_date, end_date, day_count_basis)
```

## Definition

(end_date - start_date) / day_count_basis, per [Wikipedia, Day count convention, Actual/360 and Actual/365 Fixed](https://en.wikipedia.org/wiki/Day_count_convention).

## Example

`=LEMMA.YEAR_FRACTION(46023, 46113, 360)` returns 0.25 (90 days on actual/360).

## When not to use it

- Bond conventions such as 30/360 or Actual/Actual ICMA.
- Business-day counts.
