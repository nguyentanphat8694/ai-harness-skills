# Assessment and improvement suggestions (IMP)

For every REQ/BR/FN, besides recording **what the legacy app does**, ask: is this correct, complete, consistent, and sensible for today's business? If not, create an IMP.

**Golden rule: legacy statements stay as they are; suggestions live only in IMP.** Never edit a legacy REQ to be "more right" and never silently apply a suggestion to the new app's requirements. The user decides.

Problem types: Logic error - Missing validation/edge case - Cross-screen inconsistency - Data-integrity risk - Security/permissions - Concurrency - Performance - UX/usability - Outdated (standard/regulation/algorithm changed) - Domain rule needing expert confirmation - Legacy technology. Severity: High | Medium | Low.

Format: `assets/templates/imp.md`.

Process:
1. Create the IMP as `PROPOSED`, add it to `IMPROVEMENTS.md` (sorted by severity), and set `Assessment` + IMP link on the source REQ/BR/FN.
2. `ACCEPTED` -> create a REQ `Origin: CHANGED` replacing the original (see [change-handling.md](change-handling.md)); the IMP points to the new REQ.
3. `REJECTED` -> the original REQ gets `Decision: Keep`; record the reason in the IMP.
4. `DEFERRED` -> keep the original REQ; leave the IMP for a later round.

Keep suggestions valuable: raise one only with evidence or a clear argument; do not confuse style differences with defects; if unsure it is wrong, assess `Suspect` and open a question rather than asserting; one problem per IMP. Medical, financial and legal topics must be presented as suggestions needing expert confirmation.
