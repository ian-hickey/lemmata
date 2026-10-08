# LEMMA.LOAN_BALANCE

Principal still owed on a level-payment loan after a given number of payments: the present value of the payments that remain.

```
=LEMMA.LOAN_BALANCE(principal, rate, periods, payments_made)
```

## Definition

payment * (1 - (1 + rate) ^ -(periods - payments_made)) / rate, with payment from LEMMA.LOAN_PAYMENT; principal * (1 - payments_made / periods) when rate is 0, per [Wikipedia, Amortization calculator](https://en.wikipedia.org/wiki/Amortization_calculator).

## Example

`=LEMMA.LOAN_BALANCE(200000, 0.004166666666666667, 360, 12)` returns 197049 (30 year mortgage after 12 payments).

## When not to use it

- Loans with extra or missed payments.
- Interest-only or balloon loans.
