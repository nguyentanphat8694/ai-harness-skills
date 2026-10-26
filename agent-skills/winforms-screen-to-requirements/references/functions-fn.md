# Characteristic business functions (FN)

An FN is any place the app **calculates, derives or reshapes data** from input instead of storing it as typed. Examples: last-period date -> due date and gestational age; birth date -> age; weight + height -> BMI; qty x price - discount + tax -> amount; code -> displayed name; classification by threshold; document-number generation; rounding; unit conversion; working-day/deadline calculation.

These are the easiest thing to get wrong in a rewrite because formula, rounding and edge cases live only in code. **Each one gets its own FN entry**, never just a line in a business-rule table.

Conventions:
- ID `FN-<MODULE>-<nnn>`; details live in the unit that **owns** the function (section 8 of the unit spec). A helper used on several screens is owned by an `SVC` unit; screens just link to the FN.
- `FUNCTIONS.md` is a lookup list (one line per FN: ID, business name, module, owner unit, using units, input -> output, assessment); it does not duplicate the detail.
- Entry format: `assets/templates/fn.md`.
- Test vectors: >=3, at least one edge case. State where each result comes from: derived from code / executed in a script / confirmed by user. If it can be reproduced with a short script, run it to check.

Worked example (numbers self-checked): an exam screen has `dtpDueDate.Value = dtpLastPeriod.Value.AddDays(280)`.
- Vectors: `2026-01-01 -> 2026-10-08`; `2026-03-31 -> 2027-01-05`.
- Observation: if another place (e.g. a report) uses "minus 3 months, plus 7 days, plus 1 year", then `2026-03-31` gives `2027-01-07`, 2 days off the 280-day method. That is a **cross-screen inconsistency**: record it as an IMP.
- The hard-coded 280 ignores cycles other than 28 days and does not block future dates: IMP of type "domain rule needing expert confirmation".
