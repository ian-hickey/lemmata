# LEMMA.PERCENT_OF_TOTAL

Share of a total represented by a part: part / total, returned as a decimal.

```
=LEMMA.PERCENT_OF_TOTAL(part, total)
```

## Definition

part / total, per [Wikipedia, Percentage](https://en.wikipedia.org/wiki/Percentage).

## Example

`=LEMMA.PERCENT_OF_TOTAL(25, 100)` returns 0.25 (a quarter).

## When not to use it

- Shares of a negative total.
- Allocations that must sum exactly to the total after rounding.
