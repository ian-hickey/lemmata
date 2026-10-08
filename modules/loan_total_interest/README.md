# LEMMA.LOAN_TOTAL_INTEREST

Total interest paid over the life of a level-payment loan: payment times the number of payments, less the principal.

```
=LEMMA.LOAN_TOTAL_INTEREST(principal, rate, periods)
```

## Definition

LEMMA.LOAN_PAYMENT(principal, rate, periods) * periods - principal, per [Wikipedia, Amortization calculator](https://en.wikipedia.org/wiki/Amortization_calculator).

## Example

`=LEMMA.LOAN_TOTAL_INTEREST(200000, 0.004166666666666667, 360)` returns 186512 (30 year mortgage at 5 percent on 200,000).

## When not to use it

- Loans repaid early. Interest to date is the sum of LEMMA.LOAN_INTEREST_PORTION over the payments made.
- Fees and charges, which are not interest.
