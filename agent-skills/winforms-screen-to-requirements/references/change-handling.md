# Handling changes made in conversation

## User adds, changes or drops a requirement ("the new app also needs X", "change this to...", "drop that")
0. Run `state.py check`, find the affected unit, allocate IDs with `state.py next-id`. Finish with `state.py log` + `state.py index`.
1. Identify the affected unit/module (create a new unit for entirely new functionality; `Origin: NEW`).
2. **Keep legacy requirements untouched.** For a change: create a new REQ `Origin: CHANGED` pointing at the original (`replaces REQ-...`) and set the original `Status: SUPERSEDED`. For a drop: set `Status: DROPPED` with reason and date.
3. Impact review: other units, business rules, data, permissions. Ask only if it contradicts another requirement or is too vague to write acceptance criteria; at most one question.
4. Log in `CHANGELOG.md` (date, REQ, kind of change, requested by the user, reason).
5. NEW requirements get verifiable acceptance criteria to the same standard as legacy, and sit in section 15 of the unit so "kept from legacy" and "new" are clearly separate.

## User answers an open question or settles a decision
Read STATE first. For an answered question: set the related REQ/BR `Confidence` to `Certain (user confirmed, <date>)`, set `Q-nnn` to `ANSWERED` with the answer (do not delete the row), and amend requirement text if the answer changes understanding. For a settled quirk or IMP: update `Decision` (Keep/Drop) or the IMP `Status` per the IMP process. Then CHANGELOG and STATE as usual.
