# Qodo value

Owned by the lead. One line per mission PR, written at its close. Only the first review on the same snapshot as the cold review is a fair comparison. With `QODO_REVIEW=off`, the line says `Qodo off`.

Fields: same snapshot or not · first-review findings · already caught by the cold review · new and valid, with severities · dismissed · round findings · minutes to the first review.

Example: `PR #12 · same snapshot · first review: 7 findings, 4 already caught, 2 new (1 high, 1 low), 1 dismissed · rounds: 1 new · 6 min`

## Lines

- PR #2 · same snapshot · first review: 5 findings, 4 already caught, 1 new (1 Remediation recommended), 1 dismissed · rounds: 0 new · 2 min
- PR #3 · same snapshot · first review: 2 findings, 0 already caught, 2 new (2 Remediation recommended), 0 dismissed · rounds: 0 new (round 1 and final check clean) · 2 min
- PR #4 · same snapshot · first review: 0 findings, 0 already caught, 0 new, 0 dismissed · rounds: 0 new (final check: no re-review of owner commit ad67877; scoped cold review 1 instead) · 1 min
- PR #6 · same snapshot · first review: 0 findings, 0 already caught, 0 new, 0 dismissed · rounds: 0 new · 1 min
- PR #7 · same snapshot · first review: 0 findings, 0 already caught, 0 new, 0 dismissed · rounds: 0 new (final check: no re-review of record commit 8668477) · 1.5 min
- PR #8 · same snapshot · first review: 3 findings, 1 already caught, 2 new (2 Remediation recommended), 0 dismissed · rounds: 0 new · 3 min · draft
