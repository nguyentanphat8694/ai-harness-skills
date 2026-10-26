---
name: winforms-screen-to-requirements
description: Reverse-engineer a legacy WinForms app (C#/VB.NET) into a complete requirements document set, one screen at a time. The user hands over the source and then shows screens (screenshot, caption, menu or button name); the agent locates the form in the source, traces everything it touches (base forms, UserControls, BLL/DAL, SQL and stored procedures, reports, config, permissions, devices), and writes traceable requirements, business rules, calculated-field formulas with test vectors, and an assessment of flaws in the old app. Findings accumulate into one doc set with app-level documents (overview, navigation, data model, role matrix, workflows) and a final SRS, so a new team can rebuild the app without opening the old source. Use whenever the user mentions reading, analysing or documenting a screen/form of an old WinForms app, shares a screenshot of a legacy desktop app, asks to "extract requirements", "document the legacy app", "reverse-engineer this form", "what does this screen do", wants to rewrite or migrate a WinForms/.NET Framework app, or adds/changes/drops requirements for the new app while studying the old one, even if they never say "requirements". Also use for "what is left to read", coverage, or building the final SRS from the analysed screens. Vietnamese triggers: "đọc màn hình/form X", "phân tích giao diện này", "viết requirement từ source cũ", "màn hình này làm gì", "còn màn hình nào chưa đọc", "chốt requirement để viết lại app".
---

# WinForms Screen -> Requirements

## Goal

Turn legacy WinForms source into documentation **detailed enough for another team to rebuild the app without opening the old source**, without missing any behavior. The user drives: they hand over the source, then point at screens one by one. You read each screen in depth, trace everything it depends on, and merge the result into one growing document set for the whole app.

You act as a **business analyst reading code**: record what the system must do, not a code review. Because the goal is "miss nothing", record every observable behavior, including odd behavior and old bugs, each with a decision (Keep / Drop / Ask) instead of silently skipping it.

## How the pieces fit

```
Phase A  Bootstrap (once)      inventory of the whole app, app overview, navigation skeleton
Phase B  Screen loop (repeat)  user shows a screen -> find -> trace -> unit spec -> gate -> update app-level docs
Phase C  Synthesis (at the end) assemble SRS.md, close gaps, consistency pass
```

Output goes to `requirements-docs/` (layout in [references/concepts-and-layout.md](references/concepts-and-layout.md)). State, hashes and ID counters live in `STATE.json`, managed by `scripts/state.py`.

## Start of every session

1. Find `requirements-docs/STATE.json`. Missing -> do **Phase A**. Present -> `python3 scripts/state.py --root requirements-docs check` and act on the result (doc edited outside the skill, source drift, IN_PROGRESS unit to resume). Details: [references/state-protocol.md](references/state-protocol.md).
2. Decide what the user is asking:

| User does | You do | Read |
|---|---|---|
| Hands over source for the first time | Phase A bootstrap | [references/app-level.md](references/app-level.md) |
| Shows a screen (image or name) | Phase B per-screen workflow | [references/screen-workflow.md](references/screen-workflow.md) |
| Adds / changes / drops a requirement, answers a question, settles an IMP | Change handling | [references/change-handling.md](references/change-handling.md) |
| Asks "what's left", coverage, or says reading is done | Coverage report / Phase C | [references/app-level.md](references/app-level.md) |
| Moves to scanning the whole project in one pass or planning the rewrite | Use together with the `legacy-app-ba-extractor` skill if available, sharing `requirements-docs/` | |

Scripts and templates are run/copied, not memorised: every script has `--help`. All `scripts/...`, `references/...` and `assets/...` paths in this skill are relative to **this skill's directory**; resolve them to absolute paths before running (e.g. `python3 <skill-dir>/scripts/state.py --root requirements-docs check`). Do not run them with `python3 -I` (it hides the sibling `_common.py`). `--root` and `--source` are relative to the current working directory; STATE stores `source_root` as an absolute path so later sessions can run from anywhere.

## Phase B in brief (full steps in screen-workflow.md)

0. **Load state** (`state.py check`). A DONE unit with unchanged source is answered from its file, not re-read.
1. **Identify the screen.** From a screenshot: read every visible string (title, labels, buttons, column headers, menu path) and run `scripts/find_screen.py` with them; pick the best match, state the assumption, continue. Cross-check the image against the Designer/code afterwards: the screenshot reveals visible/enabled states, defaults and dynamic controls the code alone hides.
2. **Trace to the leaves.** `scripts/trace_deps.py <Form>` gives mechanical leads; then read each lead following [references/tracing-checklist.md](references/tracing-checklist.md) until you reach DB, file, device or external API. Logic in base forms belongs to the form.
3. **Split into units** by business concern (form keeps UI orchestration; logic goes to `SVC` units). Register with `state.py register` (blocks duplicates).
4. **Write the unit spec** from `assets/templates/unit.md` in parts; checkpoint after each part. Calculated/auto-filled fields each get a full FN ([references/functions-fn.md](references/functions-fn.md)). Anything questionable gets an IMP ([references/improvements-imp.md](references/improvements-imp.md)).
5. **Gate**: `scripts/check_unit.py` (mechanical) plus the judgment checklist in screen-workflow.md. Only then `DONE`; otherwise `PARTIAL` with open questions.
6. **Update bookkeeping and app-level docs** (navigation, data model, roles, config, workflows, glossary), `state.py commit`, `state.py index`, then report.

## Rules that matter most (and why)

- **Search with `scripts/search_code.py`, not raw `grep`.** Legacy trees often contain UTF-16 or legacy-code-page files that raw grep silently skips; "not found" from grep is not evidence. Before claiming something is missing or lives in a DLL, follow [references/decompile.md](references/decompile.md).
- **Never modify the legacy source.** You only read it and write docs.
- **Every legacy requirement cites `file:method:line`.** Without a source it is not a legacy requirement; this is what keeps the docs honest and lets later sessions detect drift.
- **Legacy statements stay as found; suggestions live only in IMP.** The user decides what the new app does; silently "fixing" the old behavior would hide it from them.
- **Do not guess intent.** Assume reasonably and say so; put genuinely unknown business intent in Open Questions with `Confidence: Ask`. Do not ask many questions up front; gather them in `OPEN-QUESTIONS.md`.
- **Write as you go and via the scripts.** Checkpoints and hashes are what make interrupted or multi-session work safe; do not hand-edit `STATE.json` or `INDEX.md`.
- **One truth, one place.** Shared facts live in the owner unit/document; elsewhere link by ID.
- **Report progress for big screens** ("main form done, now tracing the pricing BLL"), and keep the final reply short: what was read, counts, notable findings, proposed next screens, coverage. Do not paste whole files into chat; give paths.
- **Language**: documents are written in English by default (or the language the user chooses, recorded as `doc_language`). Keep original class/method/table/column names and original message strings verbatim for traceability, with a translation beside non-English UI text.

## Resources

- `scripts/` (Python 3 stdlib only): `state.py` (init, check, next-id, register, set, flag, commit, log, index), `inventory.py`, `find_screen.py`, `trace_deps.py`, `check_unit.py`, `build_srs.py`, `search_code.py` (encoding-safe search), `enums.py`, `assemblies.py`.
- `references/`: concepts-and-layout, screen-workflow, tracing-checklist, functions-fn, improvements-imp, change-handling, state-protocol, app-level, decompile (encodings, enums, binaries).
- `assets/templates/`: unit, requirement, fn, imp, module, ledgers and the app-level document skeletons.
