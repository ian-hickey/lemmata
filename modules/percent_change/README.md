# LEMMA.PERCENT_CHANGE

Change from an old value to a new value as a share of the old value's magnitude: (new_value - old_value) / ABS(old_value).

```
=LEMMA.PERCENT_CHANGE(old_value, new_value)
```

## Definition

(new_value - old_value) / ABS(old_value), per [Wikipedia, Relative change](https://en.wikipedia.org/wiki/Relative_change).

## Example

`=LEMMA.PERCENT_CHANGE(100, 110)` returns 0.1 (up 10 percent).

## When not to use it

- Percentage-point differences between two rates.
- Values on a scale without a meaningful zero, such as temperatures in Celsius.
