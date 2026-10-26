# Per-screen workflow (Steps 0-6)

## Contents
- Step 0: load state
- Step 1: identify the screen (text or screenshot)
- Step 2: trace dependencies to the leaves
- Step 3: split into modules/units
- Step 4: write the unit spec
- Step 5: "nothing missed" gate
- Step 6: update bookkeeping and report

## Step 0 - Load state
`python3 scripts/state.py --root <root> check` and read the result. Handle: docs edited outside the skill (merge, never overwrite), source drift (unit goes STALE; list dependents and tell the user; do not mass-mark), IN_PROGRESS units (resume from `checkpoint` before new work). Check whether the requested screen and its dependencies are already analysed. A `DONE` unit with unchanged source is not re-analysed from scratch: read only what the new request needs, add what is missing, log it. If the user only asks about a DONE screen, answer from its unit file.

No source path known: search the workspace/uploads; if none, ask exactly one question for the path. If a DB script/backup exists, record it so SPs/triggers can be read.

No file-writing tools: return each file's content in chat with its target path.

## Step 1 - Identify the screen

### From text
The user may give a Form name, caption, menu name or button name. Search in this order: file/class name -> `Text = "caption"` in `*.Designer.cs`/`*.resx` -> menu item that opens a Form -> strings in code. Use `scripts/find_screen.py`.

### From a screenshot (preferred when the user shows the UI)
1. Read every distinct visible string off the image: window title, tab headers, group-box titles, field labels, button captions, grid column headers, status-bar text, and the menu path if visible.
2. Run `python3 scripts/find_screen.py --source <src> "<string 1>" "<string 2>" ...`. It ranks forms by how many strings they contain (diacritics/case-insensitive). A form matching most strings is the answer; one matching a single common word ("Save") is noise.
3. Several candidates: choose the best score, **state the assumption**, and continue; do not stop to ask. Ask one question only if two candidates are genuinely tied.
4. If nothing matches, the UI is probably built dynamically or text comes from a DB/resource table: search `resx`, localization tables, and the menu/permission table, then trace from the menu entry.
5. Save the screenshot under `screenshots/<UNIT-ID>.png` when you can, and reference it in the unit.
6. **Cross-check the image against the Designer/code.** The image shows what the designer is actually seeing: values in dropdowns, default values, which controls are visible/enabled in that state, dynamically created controls, localized captions, grid columns. Record mismatches (controls in code but not on screen, or the reverse) as legacy quirks or open questions: they often reveal permission-driven or state-driven visibility.
7. Ask the user for nothing the code can tell you. Ask for sample/real data only where behavior depends on data you cannot see (lookup contents, thresholds stored in a table).

Useful commands (adjust for C#/VB):
```bash
grep -rln ": Form\|: BaseForm\|Inherits .*Form" --include=*.cs --include=*.vb .
grep -rn 'Text = "Caption"' --include=*.Designer.cs .
grep -rn "new FrmX\|FrmX\.Show\|FrmX()" --include=*.cs --include=*.vb .   # who opens this form
```

## Step 2 - Trace dependencies to the leaves
Start with `python3 scripts/trace_deps.py --source <src> <FormClass>` for a mechanical list of leads (handlers, forms opened, BLL calls, SQL/SP, messages, shortcuts, timers, global state, permissions, computed fields, who opens this form). Then read each lead. Follow every direction until a leaf (DB, file, device, external API). The full checklist is in [tracing-checklist.md](tracing-checklist.md).

If a symbol cannot be found (enum, class, constant): use `search_code.py`, then [decompile.md](decompile.md). Never write "lives in a DLL" before an encoding-safe search and `assemblies.py` agree.

Each thing found becomes a unit or attaches to an existing one; record caller/callee relations for `MODULE.md`.

Large code-behind files (thousands of lines): read by `#region`/segment and **write into the unit file after each segment**, updating `checkpoint` in STATE each time.

## Step 3 - Split into modules/units
- Assign each unit to a business module; create the module (and list it in INDEX) if new.
- A screen that touches several concerns (e.g. a sales form with stock, receivables, printing) is **split**: the form keeps UI orchestration; business logic lives in the matching `SVC` unit.
- Names use business terms; the old class name goes in the Source section and `aliases`.
- Register: `python3 scripts/state.py register <UNIT-ID> --alias <name> --dep <UNIT-ID> --inventory <key>`. With `--inventory` it records **every file of the form** (code-behind, `.Designer.cs`, `.resx`) as a source, so a later change to the layout is detected as drift. Add other files the unit depends on (BLL/DAL, SP scripts) with repeated `--source <relpath>`. It refuses a second unit for the same alias. `check_unit.py` fails if a form's Designer/resx exists on disk but is not registered.

## Step 4 - Write the unit spec
Create/update `modules/<MODULE>/units/<UNIT-ID>.md` from `assets/templates/unit.md`. Write after each completed part; set status via `state.py set <UNIT> IN_PROGRESS --checkpoint "<what is done>"`. Requirement format: `assets/templates/requirement.md`. Write from the business perspective ("the system must ... because ...") without dropping behavior: control names, tab order and display formats that affect users go in the UI inventory and Coverage table. Do not invent schema or pick frameworks for the new app unless asked. Do not guess: unclear intent -> `Confidence: Ask` + Open Question.

## Step 5 - "Nothing missed" gate
A unit is `DONE` only when all of these hold:

- [ ] Every event handler (incl. base form and child controls) is in the Coverage table, each pointing to >=1 REQ or marked "no business logic" with a reason.
- [ ] Every behavior-bearing control (inputs, buttons, grids, menus, context menus, shortcuts) is in the UI inventory.
- [ ] Every SQL/SP/DataSet call is in Data access: tables, read/write, filters, sort, transaction.
- [ ] Every MessageBox/custom message/error is in Messages with its trigger condition (messages usually state a business rule).
- [ ] Every validation, calculation and enable/disable/show/hide condition became a business rule.
- [ ] Every data state and transition (draft -> approved -> cancelled...) is listed.
- [ ] Permissions, audit/log, concurrency (row lock, version check), transaction/rollback considered (write "none" if none).
- [ ] Hidden behavior reviewed (tracing-checklist item 11).
- [ ] Every auto-calculated/auto-filled field has a complete FN (formula, edge cases, test vectors).
- [ ] Every REQ/BR/FN has an Assessment; anything not `OK` links an IMP.
- [ ] No duplicate IDs; no two REQs share the same `file:method` source; STATE matches the unit file.
- [ ] Every dependent unit is registered in STATE (analysed or `PENDING`), none left dangling.
- [ ] If a screenshot was supplied, it was cross-checked against the Designer/code.

Run the mechanical part: `python3 scripts/check_unit.py --source <src> --root <root> <UNIT-ID> <FormClass>` (exit 1 = fix and rerun). The rest is judgment; do it honestly. Anything unreadable (missing source, closed DLL, SP without script): record it in Open Questions and mark the unit `PARTIAL`, never pretend it is complete.

## Step 6 - Update bookkeeping and report
Commit order (also in [state-protocol.md](state-protocol.md)): `FUNCTIONS.md`, `IMPROVEMENTS.md`, `MODULE.md`, app-level docs touched (see [app-level.md](app-level.md)), `OPEN-QUESTIONS.md`, `GLOSSARY.md`, `CHANGELOG.md`; then `python3 scripts/state.py commit <UNIT> --status DONE|PARTIAL --note "..."` and `python3 scripts/state.py index`.

Then reply briefly in this shape:
1. Screen read; units found (ID + type) and their modules.
2. Counts: requirements / business rules / FN extracted, open questions, unit status.
3. Notable findings (odd behavior, hidden rules, contradictions) and proposed IMPs (High first) for the user to accept/reject.
4. Related screens/units found but not read, proposed as next steps (user decides).
5. Coverage line (e.g. "14/62 screens DONE") and, from the screenshot cross-check, any mismatches.

Do not paste whole requirement files into chat; summarize and give paths.
