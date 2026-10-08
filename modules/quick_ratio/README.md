# LEMMA.QUICK_RATIO

Quick ratio: (current_assets - inventory) / current_liabilities, a liquidity measure that excludes inventory.

```
=LEMMA.QUICK_RATIO(current_assets, inventory, current_liabilities)
```

## Definition

(current_assets - inventory) / current_liabilities, per [Wikipedia, Quick ratio](https://en.wikipedia.org/wiki/Quick_ratio).

## Example

`=LEMMA.QUICK_RATIO(150000, 30000, 100000)` returns 1.2 (covered 1.2 times).

## When not to use it

- Current ratio, which keeps inventory. Use LEMMA.CURRENT_RATIO.
- Companies with no current liabilities, where the ratio is undefined.
