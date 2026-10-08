# LEMMA.LOAN_INTEREST_PORTION

Interest included in one payment of a level-payment loan: the balance before that payment times the rate per period.

```
=LEMMA.LOAN_INTEREST_PORTION(principal, rate, periods, period)
```

## Definition

LEMMA.LOAN_BALANCE(principal, rate, periods, period - 1) * rate, per [Wikipedia, Amortization schedule](https://en.wikipedia.org/wiki/Amortization_schedule).

## Example

`=LEMMA.LOAN_INTEREST_PORTION(200000, 0.004166666666666667, 360, 1)` returns 833.333 (first payment of a 30 year mortgage).

## When not to use it

- Loans with payments in advance or irregular payments.
- Daily-accrual interest between payment dates.
