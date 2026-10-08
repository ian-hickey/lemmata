# LEMMA.CURRENT_RATIO

Current ratio: current_assets / current_liabilities, a liquidity measure.

```
=LEMMA.CURRENT_RATIO(current_assets, current_liabilities)
```

## Definition

current_assets / current_liabilities, per [Wikipedia, Current ratio](https://en.wikipedia.org/wiki/Current_ratio).

## Example

`=LEMMA.CURRENT_RATIO(150000, 100000)` returns 1.5 (one and a half times).

## When not to use it

- Quick ratio, which excludes inventory.
- Companies with no current liabilities, where the ratio is undefined.
