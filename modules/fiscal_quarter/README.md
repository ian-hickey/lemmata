# LEMMA.FISCAL_QUARTER

Fiscal quarter, 1 to 4, containing a date, for a fiscal year starting in a given month.

```
=LEMMA.FISCAL_QUARTER(date, start_month)
```

## Definition

INT(MOD(MONTH(date) - start_month, 12) / 3) + 1, per [Wikipedia, Fiscal year](https://en.wikipedia.org/wiki/Fiscal_year).

## Example

`=LEMMA.FISCAL_QUARTER(46249, 7)` returns 1 (august in a july fiscal year is q1).

## When not to use it

- Quarters of unequal length, such as 4-4-5 retail calendars.
- Fiscal years that start mid-month.
