# LEMMA.PERPETUITY_PV

Present value of a payment that recurs forever, starting one period from now and growing at a constant rate: payment / (rate - growth).

```
=LEMMA.PERPETUITY_PV(payment, rate, growth)
```

## Definition

payment / (rate - growth), per [Wikipedia, Perpetuity](https://en.wikipedia.org/wiki/Perpetuity).

## Example

`=LEMMA.PERPETUITY_PV(100, 0.05, 0)` returns 2000 (level perpetuity of 100 at 5 percent).

## When not to use it

- A stream that ends. Use LEMMA.ANNUITY_PV.
- Growth at or above the discount rate, which has no finite value.
