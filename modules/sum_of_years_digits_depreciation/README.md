# LEMMA.SUM_OF_YEARS_DIGITS_DEPRECIATION

Depreciation charged in a given period under the sum-of-years-digits method, which front-loads the charge over a whole-number life.

```
=LEMMA.SUM_OF_YEARS_DIGITS_DEPRECIATION(cost, salvage, life, period)
```

## Definition

(cost - salvage) * (life - period + 1) / (life * (life + 1) / 2), per [Wikipedia, Depreciation, sum-of-years-digits method](https://en.wikipedia.org/wiki/Depreciation#Sum-of-years-digits_method).

## Example

`=LEMMA.SUM_OF_YEARS_DIGITS_DEPRECIATION(30000, 7500, 10, 1)` returns 4090.91 (microsoft syd example, first year).

## When not to use it

- A fractional life, which this method does not define.
- Tax schedules with half-year conventions.
