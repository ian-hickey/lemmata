# LEMMA.UNITS_OF_PRODUCTION_DEPRECIATION

Depreciation charged in a period under the units-of-production method: (cost - salvage) times the share of total expected output produced in the period.

```
=LEMMA.UNITS_OF_PRODUCTION_DEPRECIATION(cost, salvage, total_units, units_in_period)
```

## Definition

(cost - salvage) * units_in_period / total_units, per [Wikipedia, Depreciation, units-of-production method](https://en.wikipedia.org/wiki/Depreciation#Units-of-production_depreciation_method).

## Example

`=LEMMA.UNITS_OF_PRODUCTION_DEPRECIATION(50000, 5000, 100000, 12000)` returns 5400 (machine rated for 100,000 units).

## When not to use it

- Time-based methods. Use LEMMA.STRAIGHT_LINE_DEPRECIATION.
- Output beyond the original estimate, which needs a revised total_units.
