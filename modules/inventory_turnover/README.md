# LEMMA.INVENTORY_TURNOVER

Inventory turnover: cost_of_goods_sold / average_inventory for the period, the number of times inventory was sold through.

```
=LEMMA.INVENTORY_TURNOVER(cost_of_goods_sold, average_inventory)
```

## Definition

cost_of_goods_sold / average_inventory, per [Wikipedia, Inventory turnover](https://en.wikipedia.org/wiki/Inventory_turnover).

## Example

`=LEMMA.INVENTORY_TURNOVER(600000, 100000)` returns 6 (six turns).

## When not to use it

- Revenue-based turnover, which mixes selling prices with costs.
- Businesses with no inventory.
