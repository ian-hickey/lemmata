# LEMMA.ANNUITY_FV

Future value at the end of the last period of a level payment made at the end of each period (an ordinary annuity).

```
=LEMMA.ANNUITY_FV(payment, rate, periods)
```

## Definition

payment * ((1 + rate) ^ periods - 1) / rate, or payment * periods when rate is 0, per [Wikipedia, Annuity, future value of an annuity-immediate](https://en.wikipedia.org/wiki/Annuity#Future_value_of_an_annuity-immediate).

## Example

`=LEMMA.ANNUITY_FV(100, 0.05, 10)` returns 1257.79 (100 per period for ten periods at 5 percent).

## When not to use it

- Payments at the start of each period (an annuity due).
- A lump sum. Use LEMMA.FUTURE_VALUE.
