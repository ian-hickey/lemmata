# LEMMA.NET_MARGIN

Net profit margin as a share of revenue: net_income / revenue, returned as a decimal.

```
=LEMMA.NET_MARGIN(revenue, net_income)
```

## Definition

net_income / revenue, per [Wikipedia, Profit margin](https://en.wikipedia.org/wiki/Profit_margin).

## Example

`=LEMMA.NET_MARGIN(1000000, 80000)` returns 0.08 (8 percent margin).

## When not to use it

- Operating margin, which excludes interest and tax. Use LEMMA.OPERATING_MARGIN.
- Margins of a single product line, where allocated overhead decides the answer.
