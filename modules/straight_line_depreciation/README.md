# LEMMA.STRAIGHT_LINE_DEPRECIATION

Depreciation charged in each period under the straight-line method: (cost - salvage) / life.

```
=LEMMA.STRAIGHT_LINE_DEPRECIATION(cost, salvage, life)
```

## Definition

(cost - salvage) / life, per [Wikipedia, Depreciation, straight-line method](https://en.wikipedia.org/wiki/Depreciation#Straight-line_depreciation).

## Example

`=LEMMA.STRAIGHT_LINE_DEPRECIATION(30000, 7500, 10)` returns 2250 (microsoft sln example).

## When not to use it

- Accelerated methods. Use LEMMA.DECLINING_BALANCE_DEPRECIATION or LEMMA.SUM_OF_YEARS_DIGITS_DEPRECIATION.
- Tax schedules such as MACRS, which follow published tables.
