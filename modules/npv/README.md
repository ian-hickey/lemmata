# LEMMA.NPV

Net present value of evenly spaced cash flows, with the timing of the first cash flow stated as an argument.

```
=LEMMA.NPV(rate, cashflows, first_period)
```

## Definition

NPV = Σ cashflows[i] / (1 + rate)^(first_period + i), summing from i = 0. With `first_period` = 1 this is exactly [Excel's NPV](https://support.microsoft.com/en-us/office/npv-function-8672cb67-2576-4d07-b67b-ac28acf2a568), which assumes the first cash flow lands at the end of period 1. With `first_period` = 0 the first cash flow is today.

The timing argument exists because the Excel default is a common source of error: an initial investment placed in the first cell gets discounted by one period when it should not be.

## Example

An investment of 40,000 today returning 8,000, 9,200, 10,000, 12,000, and 14,500 at the end of each of the next five years, discounted at 8 percent:

`=LEMMA.NPV(0.08, B1:B6, 0)` with B1:B6 holding -40000, 8000, 9200, 10000, 12000, 14500 returns 1922.06.

## When not to use it

- Cash flows on irregular dates. Use an XNPV-style module with explicit dates.
- A discount rate that changes over time.
- A range with blanks. A blank is an error here, not a zero, because a blank usually means a missing value.
- A single number instead of a range. Excel accepts it, but IronCalc, which runs the tests, does not, so the module is only specified for ranges.
