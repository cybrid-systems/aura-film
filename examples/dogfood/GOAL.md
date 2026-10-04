# aura-film dogfood — success predicate

Write a small **Aura Soft** program that maps a year onto the 24-hour
invention clock and prints these lines (each plus a trailing newline):

```
BEAT id=cave clock=23:40:00.000
BEAT id=here clock=00:00:00.000
YOU ARE HERE
FILM_M0_OK
```

## Semantics

- Now is year 2026, the end of the day, displayed `00:00:00.000`.
- 45,000 years before now is exactly 20 minutes before that midnight, so
  year `-42974` is `23:40:00.000`.
- `ms_before = years_ago * 80 / 3` with integer division.
- The day is `86400000` ms and `3240000` years.
- Must define `(define (film:clock-ms …) …)` and use it. Hardcoding only
  the display lines is a fail.

## Why stub starts wrong

The stub divides by 4 instead of 3, so cave art is not 23:40.
