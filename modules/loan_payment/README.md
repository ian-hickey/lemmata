# LEMMA.LOAN_PAYMENT

The level payment that repays a loan in full over a fixed number of periods.

```
=LEMMA.LOAN_PAYMENT(principal, rate, periods)
```

## Definition

The ordinary annuity payment: principal × rate / (1 − (1 + rate)^−periods). When the rate is zero the payment is principal / periods. This is Excel's `PMT(rate, periods, principal)` with the sign flipped, per [Microsoft's PMT documentation](https://support.microsoft.com/en-us/office/pmt-function-0214da64-9a63-4996-bc20-214433fa6441).

## Example

A 200,000 loan at 5 percent per year, repaid monthly over 30 years:

`=LEMMA.LOAN_PAYMENT(200000, 0.05 / 12, 360)` returns 1073.64.

## When not to use it

- Payments at the start of each period (an annuity due). This module assumes payments at the end.
- A balloon or residual value at the end of the term.
- A rate that changes during the term, or a part-period at the start.
- A number of periods that is not a whole number. The module returns `#NUM!` rather than guess.
