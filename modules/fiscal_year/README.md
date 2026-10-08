# LEMMA.FISCAL_YEAR

Fiscal year containing a date, named by the calendar year in which the fiscal year ends, for a fiscal year starting in a given month.

```
=LEMMA.FISCAL_YEAR(date, start_month)
```

## Definition

YEAR(date) + 1 if MONTH(date) >= start_month and start_month > 1, else YEAR(date), per [Wikipedia, Fiscal year](https://en.wikipedia.org/wiki/Fiscal_year).

## Example

`=LEMMA.FISCAL_YEAR(46249, 7)` returns 2027 (august 2026 in a july fiscal year).

## When not to use it

- 52/53-week fiscal calendars that end on a weekday.
- Fiscal years that start mid-month.
