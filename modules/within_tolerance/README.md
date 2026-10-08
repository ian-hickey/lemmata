# LEMMA.WITHIN_TOLERANCE

TRUE when a value is within a tolerance of its target, FALSE otherwise: ABS(value - target) <= tolerance.

```
=LEMMA.WITHIN_TOLERANCE(value, target, tolerance)
```

## Definition

ABS(value - target) <= tolerance, per [Wikipedia, Approximation error](https://en.wikipedia.org/wiki/Approximation_error).

## Example

`=LEMMA.WITHIN_TOLERANCE(100.004, 100, 0.01)` returns True (within).

## When not to use it

- Relative comparisons where the tolerance scales with the values.
- Comparing text or dates by meaning.
