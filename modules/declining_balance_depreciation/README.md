# LEMMA.DECLINING_BALANCE_DEPRECIATION

Depreciation charged in a given period under the declining-balance method at a chosen factor, never taking book value below salvage.

```
=LEMMA.DECLINING_BALANCE_DEPRECIATION(cost, salvage, life, period, factor)
```

## Definition

book value at start of period * factor / life, capped at book value minus salvage, where book value = cost * (1 - factor / life) ^ (period - 1), per [Wikipedia, Depreciation, declining-balance method](https://en.wikipedia.org/wiki/Depreciation#Declining-balance_method).

## Example

`=LEMMA.DECLINING_BALANCE_DEPRECIATION(2400, 300, 10, 1, 2)` returns 480 (microsoft ddb example, first year).

## When not to use it

- Methods that switch to straight-line when it gives a larger charge, such as Excel VDB.
- Partial first periods.
