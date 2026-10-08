# LEMMA.MONTHS_BETWEEN

Whole calendar months from a start date to an end date, counting month boundaries crossed and ignoring the day of month.

```
=LEMMA.MONTHS_BETWEEN(start_date, end_date)
```

## Definition

(YEAR(end_date) - YEAR(start_date)) * 12 + MONTH(end_date) - MONTH(start_date), per [Wikipedia, Month](https://en.wikipedia.org/wiki/Month).

## Example

`=LEMMA.MONTHS_BETWEEN(45672, 46037)` returns 12 (one year).

## When not to use it

- Fractional months or exact durations. Use day counts.
- Tenor arithmetic that needs end-of-month rules.
