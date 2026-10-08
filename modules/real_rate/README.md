# LEMMA.REAL_RATE

Real rate of return from a nominal rate and an inflation rate using the exact Fisher relation: (1 + nominal) / (1 + inflation) - 1.

```
=LEMMA.REAL_RATE(nominal_rate, inflation_rate)
```

## Definition

(1 + nominal_rate) / (1 + inflation_rate) - 1, per [Wikipedia, Fisher equation](https://en.wikipedia.org/wiki/Fisher_equation).

## Example

`=LEMMA.REAL_RATE(0.08, 0.03)` returns 0.0485437 (8 percent nominal, 3 percent inflation).

## When not to use it

- The linear approximation, which overstates the real rate when inflation is high.
- Rates over different periods.
