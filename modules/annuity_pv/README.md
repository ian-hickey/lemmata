# LEMMA.ANNUITY_PV

Present value of a level payment made at the end of each period for a number of periods (an ordinary annuity).

```
=LEMMA.ANNUITY_PV(payment, rate, periods)
```

## Definition

payment * (1 - (1 + rate) ^ -periods) / rate, or payment * periods when rate is 0, per [Wikipedia, Annuity, present value of an annuity-immediate](https://en.wikipedia.org/wiki/Annuity#Present_value_of_an_annuity-immediate).

## Example

`=LEMMA.ANNUITY_PV(100, 0.05, 10)` returns 772.173 (100 per period for ten periods at 5 percent).

## When not to use it

- Payments at the start of each period (an annuity due).
- Payments that grow or vary. Use LEMMA.NPV with the actual series.
