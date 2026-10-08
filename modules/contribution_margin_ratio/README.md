# LEMMA.CONTRIBUTION_MARGIN_RATIO

Contribution margin as a share of price: (price - variable_cost) / price, returned as a decimal.

```
=LEMMA.CONTRIBUTION_MARGIN_RATIO(price, variable_cost)
```

## Definition

(price - variable_cost) / price, per [Wikipedia, Contribution margin](https://en.wikipedia.org/wiki/Contribution_margin).

## Example

`=LEMMA.CONTRIBUTION_MARGIN_RATIO(50, 30)` returns 0.4 (40 percent contribution).

## When not to use it

- Fixed costs, which this ratio ignores by design.
- Gross margin, which uses cost of goods sold rather than variable cost.
