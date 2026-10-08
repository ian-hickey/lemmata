# LEMMA.ANNUALIZED_RETURN

Return per year equivalent to a total return earned over a number of years: (1 + total_return) ^ (1 / years) - 1.

```
=LEMMA.ANNUALIZED_RETURN(total_return, years)
```

## Definition

(1 + total_return) ^ (1 / years) - 1, per [Wikipedia, Rate of return, annualisation](https://en.wikipedia.org/wiki/Rate_of_return#Annualisation).

## Example

`=LEMMA.ANNUALIZED_RETURN(0.5, 3)` returns 0.144714 (50 percent over three years).

## When not to use it

- Periods under a year when the figure will be quoted as achieved rather than projected.
- Arithmetic averages of yearly returns.
