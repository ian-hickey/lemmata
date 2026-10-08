# LEMMA.CAGR

Compound annual growth rate: the constant yearly rate that takes `start_value` to `end_value` in `years`.

```
=LEMMA.CAGR(start_value, end_value, years)
```

## Definition

CAGR = (end_value / start_value) ^ (1 / years) − 1, per [Investopedia](https://www.investopedia.com/terms/c/cagr.asp). The result is a decimal rate per year. Format the cell as a percentage to display it.

## Example

`=LEMMA.CAGR(10000, 19000, 3)` returns 0.2386, a growth rate of 23.86 percent per year.

## When not to use it

- Cash flows in between the start and end. CAGR ignores them. Use an IRR-style module for a series of flows.
- A start value of zero or below. There is no growth rate from nothing, so the module returns `#NUM!`.
- Periods measured in anything but years. Convert to years first, or the rate will be per period instead of per year.
