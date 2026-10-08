# LEMMA.MARKUP

Markup of a selling price over its cost as a share of cost: (price - cost) / cost, returned as a decimal.

```
=LEMMA.MARKUP(price, cost)
```

## Definition

(price - cost) / cost, per [Wikipedia, Markup (business)](https://en.wikipedia.org/wiki/Markup_(business)).

## Example

`=LEMMA.MARKUP(150, 100)` returns 0.5 (50 percent markup).

## When not to use it

- Margin as a share of price. Use LEMMA.GROSS_MARGIN.
- Converting between the two: markup = margin / (1 - margin).
