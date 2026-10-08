# LEMMA.LOAN_PRINCIPAL_PORTION

Principal repaid by one payment of a level-payment loan: the payment less the interest part of that payment.

```
=LEMMA.LOAN_PRINCIPAL_PORTION(principal, rate, periods, period)
```

## Definition

LEMMA.LOAN_PAYMENT(principal, rate, periods) - LEMMA.LOAN_INTEREST_PORTION(principal, rate, periods, period), per [Wikipedia, Amortization schedule](https://en.wikipedia.org/wiki/Amortization_schedule).

## Example

`=LEMMA.LOAN_PRINCIPAL_PORTION(200000, 0.004166666666666667, 360, 1)` returns 240.31 (first payment of a 30 year mortgage).

## When not to use it

- Loans with extra payments.
- Interest-only periods.
