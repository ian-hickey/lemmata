# LEMMA.NOMINAL_RATE

Nominal annual rate that, compounded a given number of times per year, yields the stated effective annual rate: periods * ((1 + effective) ^ (1 / periods) - 1).

```
=LEMMA.NOMINAL_RATE(effective_rate, periods_per_year)
```

## Definition

periods_per_year * ((1 + effective_rate) ^ (1 / periods_per_year) - 1), per [Wikipedia, Effective interest rate](https://en.wikipedia.org/wiki/Effective_interest_rate).

## Example

`=LEMMA.NOMINAL_RATE(0.12682503013196977, 12)` returns 0.12 (12.68 percent effective, monthly).

## When not to use it

- Continuous compounding, which is LN(1 + effective_rate).
- Rates per period rather than per year. Divide the result by periods_per_year for the periodic rate.
