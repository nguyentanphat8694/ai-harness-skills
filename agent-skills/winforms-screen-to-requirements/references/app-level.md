# App-level documents and phases

The per-screen workflow produces unit specs. This file covers what turns them into documentation of the *whole app*: the initial inventory, the app-level documents that stitch units together, coverage tracking, and the final synthesis.

## Contents
- Phase A: bootstrap (once per project)
- Phase B: screen-by-screen loop (see screen-workflow.md)
- App-level documents: what feeds each, when to update
- Coverage and "what next"
- Phase C: synthesis into SRS.md

## Phase A - Bootstrap (once, before the first screen)

Do this the first time the user hands over source; skip if `STATE.json` already has an `inventory`.

1. Ask at most one grouped question only for what you cannot find: source path, whether a DB script/backup exists, the documentation language (default English), and the scope (whole app or one area). Defaults are fine; state them.
2. `python3 scripts/state.py init --root requirements-docs --source <src> --lang en`
3. `python3 scripts/inventory.py --source <src> --root requirements-docs`. It lists forms, user controls, reports, SQL objects, timers/background workers and the menu items that open forms, and writes them to `STATE.json` -> `inventory`. Menu detection follows helper calls (a handler that calls `LoadControlX()` which does `new FrmX()` still counts) and is scoped per form. Handlers that open forms but are never wired to a control are reported as `unwired_handlers` (dead code or runtime wiring): list them in NAVIGATION.md as unreachable-from-menu and ask the user before spending time on them. Treat it as a heuristic start: skim the result, read `Program.cs`/`Main`, the main/MDI form and the DB scripts to fill gaps (dynamically opened forms, plug-ins, reflection, forms listed in a DB menu table).
4. Identify solution layout and tech: projects, target framework, .NET Framework vs .NET, language, UI libraries, ORM/DAL style, DB engine, reporting engine, installers, config files. Write `APP-OVERVIEW.md` (template in `assets/templates/`).
5. Seed `NAVIGATION.md` with the startup flow (Main -> login -> main form) and the menu tree from `STATE.menus`. Mark unread screens as `PENDING`.
6. Propose an initial module split (business names) in `APP-OVERVIEW.md`; it is allowed to change as screens are read. Tell the user the inventory size and invite them to point at the first screen.

Do not analyse any screen deeply during bootstrap. The point is a complete list to measure coverage against, and a skeleton to hang findings on.

## Phase B - The loop
The user shows a screen (image or text); you run `screen-workflow.md`. After each screen, also update the app-level documents below.

## App-level documents

| File | Fed by | Update after each screen |
|---|---|---|
| `APP-OVERVIEW.md` | bootstrap; module list evolves | add/rename modules, update coverage numbers |
| `NAVIGATION.md` | menu tree, "opened by" leads, `DialogResult` and parameters | add every screen-to-screen transition: from -> to, trigger (button/menu/shortcut), data passed, data returned, condition; update menu tree entries with the unit ID |
| `DATA-MODEL.md` | Data access sections of units, SQL scripts, DataSets/ORM | add or extend tables/entities: columns used, keys, relations, status columns and allowed values, who reads/writes (unit IDs), triggers/SPs touching them. Mark entities seen only through code (no schema script) as `inferred` |
| `ROLES-MATRIX.md` | Actor & permissions sections | add roles and a row per screen/function: allowed / hidden / read-only per role, and where it is enforced (UI visible flag, BLL check, SP). Never merge differing rules silently |
| `CONFIG-AND-INTEGRATIONS.md` | config/settings/registry leads, INT units | keys with meaning and effect, per-environment differences, third-party libs with licences/versions if visible, devices and external systems |
| `WORKFLOWS.md` | units' flows + NAVIGATION + DATA-MODEL | when screens A, B, C form one business process (e.g. register -> examine -> bill -> pay), write it end to end by unit ID, including status transitions of the main data object and exceptional paths |
| `GLOSSARY.md` | legacy names and domain terms | add new terms with unit references |

Rules:
- One truth, one place: put a fact in its owner document and link by ID elsewhere.
- Facts not yet confirmed by reading stay marked `inferred` or `pending (UNIT-ID)`; do not fill gaps by guessing.
- When a new screen contradicts an app-level statement, record it in the CHANGELOG as DISCREPANCY and fix the app-level doc only after verifying.

## Coverage and "what next"
`state.py index` writes the coverage line to `INDEX.md` (inventory items `DONE` / total). After each screen, report it and suggest 1-3 next screens, in this order of preference: (1) units the screen depends on that are `PENDING`; (2) screens that open or are opened by it; (3) screens writing to the same tables (shared data often hides cross-screen rules); (4) the rest of the menu. The user decides.

Inventory items that are dead code (no menu entry, never opened) are marked `orphan` in the inventory and reported once, so the user can decide to skip them.

## Phase C - Synthesis (when the user says the reading is done, or coverage is high)

1. Run `state.py check` and `state.py index`. List units that are not `DONE` (PENDING/PARTIAL/STALE), open questions, and PROPOSED IMPs. Tell the user what remains and let them choose to close or defer each.
2. Run `python3 scripts/build_srs.py --root requirements-docs` to assemble `SRS.md` mechanically (overview, navigation, roles, data model, per-module requirement summaries with links, FN catalogue, accepted improvements, open questions). The script only stitches existing content and lists gaps.
3. Read the result and add the connective prose that a script cannot: business context per module, cross-module workflows, decisions pending, and a "differences from legacy" section (CHANGED/NEW/DROPPED, ACCEPTED IMPs). Keep it in `<!-- manual:start -->` ... `<!-- manual:end -->` blocks so rebuilds preserve it.
4. Run a consistency pass: every unit referenced exists, every FN referenced is in `FUNCTIONS.md`, every table in a Data access section is in `DATA-MODEL.md`, every menu item maps to a unit or is marked orphan. Report gaps rather than hiding them.
