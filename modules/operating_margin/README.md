# LEMMA.OPERATING_MARGIN

Operating margin as a share of revenue: operating_income / revenue, returned as a decimal.

```
=LEMMA.OPERATING_MARGIN(revenue, operating_income)
```

## Definition

operating_income / revenue, per [Wikipedia, Operating margin](https://en.wikipedia.org/wiki/Operating_margin).

## Example

`=LEMMA.OPERATING_MARGIN(1000000, 150000)` returns 0.15 (15 percent margin).

## When not to use it

- Gross margin, which stops at cost of goods sold. Use LEMMA.GROSS_MARGIN.
- Net margin, which also deducts interest and tax. Use LEMMA.NET_MARGIN.
