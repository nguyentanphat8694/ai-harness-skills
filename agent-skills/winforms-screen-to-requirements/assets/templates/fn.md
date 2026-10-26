#### FN-<MOD>-<nnn> - <business name>
- **Trigger**: which event/control change runs it; automatic or button; does it re-run when an old record is opened
- **Inputs**: name | type | unit/format | required | valid range
- **Outputs**: name | type | where displayed | read-only or user-overridable | stored in DB or recomputed each time
- **Algorithm**: step by step exactly as the code does (pseudocode): how days/months/years are added, order and kind of rounding, culture/timezone, constants with their meaning
- **Edge cases and errors**: empty, bad format, out of range, leap year, future/far-past values, negatives, divide by zero - what the code does in each
- **Dependencies**: parameter tables, config, other FN
- **Test vectors** (>=3, at least one edge case): Input -> Output. State the source of each result: derived from code / executed in a script / confirmed by user.
- **Source**: file:method:line
- **Assessment**: OK | Suspect | Wrong | Missing | Outdated (not OK -> link IMP)
