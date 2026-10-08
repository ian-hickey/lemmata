# LEMMA.BREAK_EVEN_UNITS

Units that must be sold for revenue to cover fixed and variable costs: fixed_costs / (price - variable_cost).

```
=LEMMA.BREAK_EVEN_UNITS(fixed_costs, price, variable_cost)
```

## Definition

fixed_costs / (price - variable_cost), per [Wikipedia, Break-even (economics)](https://en.wikipedia.org/wiki/Break-even_(economics)).

## Example

`=LEMMA.BREAK_EVEN_UNITS(10000, 20, 12)` returns 1250 (10,000 fixed, 20 price, 12 variable).

## When not to use it

- Multiple products with different margins.
- Step fixed costs that change with volume.
