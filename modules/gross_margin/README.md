# LEMMA.GROSS_MARGIN

Gross margin: the share of revenue left after the direct cost of what was sold.

```
=LEMMA.GROSS_MARGIN(revenue, cost_of_goods_sold)
```

## Definition

Gross margin = (revenue − cost of goods sold) / revenue, per [Investopedia](https://www.investopedia.com/terms/g/grossmargin.asp). The result is a decimal share. Format the cell as a percentage to display it.

## Example

`=LEMMA.GROSS_MARGIN(200000, 150000)` returns 0.25, a 25 percent gross margin.

## When not to use it

- Gross profit in currency. This module returns a ratio; subtract the two inputs for the amount.
- Operating or net margin. Those subtract operating expenses, interest, and tax as well, which this module does not take.
- Markup. Markup divides by cost, not revenue, so a 25 percent margin is a 33 percent markup.
- Zero or negative revenue. There is no meaningful margin on no sales, so the module returns `#NUM!`.
