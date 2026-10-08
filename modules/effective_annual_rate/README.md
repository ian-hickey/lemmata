# LEMMA.EFFECTIVE_ANNUAL_RATE

Effective annual rate from a nominal annual rate compounded a given number of times per year: (1 + nominal / periods) ^ periods - 1.

```
=LEMMA.EFFECTIVE_ANNUAL_RATE(nominal_rate, periods_per_year)
```

## Definition

(1 + nominal_rate / periods_per_year) ^ periods_per_year - 1, per [Wikipedia, Effective interest rate](https://en.wikipedia.org/wiki/Effective_interest_rate).

## Example

`=LEMMA.EFFECTIVE_ANNUAL_RATE(0.12, 12)` returns 0.126825 (12 percent monthly).

## When not to use it

- Continuous compounding, which is EXP(nominal_rate) - 1.
- Converting an effective rate back. Use LEMMA.NOMINAL_RATE.
