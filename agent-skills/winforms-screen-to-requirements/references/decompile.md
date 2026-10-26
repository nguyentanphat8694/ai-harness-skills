# Missing logic: encodings, enums, and logic that lives in binaries

Requirements are only as complete as what you can read. Three things hide logic from a text search of the source. Check all three during bootstrap and whenever a symbol "cannot be found".

## Contents
- 1. A symbol "cannot be found": check encoding first
- 2. Enums and constants
- 3. Assemblies you cannot read as source
- 4. Decompiling an own-code DLL
- 5. What to record when you cannot recover the logic

## 1. A symbol "cannot be found": check encoding first

Never conclude "it is not in the source" from a raw `grep`/`rg` that returned nothing. Legacy .NET trees mix encodings:

| Encoding | Looks like | Raw grep sees |
|---|---|---|
| UTF-16 (BOM `FF FE`) | normal in an editor | `p\0u\0b\0l\0i\0c\0` so ASCII text never matches |
| Windows-1258 / 1252 | Vietnamese or accented text saved in a legacy code page | accented words do not match their UTF-8 form |
| UTF-8 with BOM | fine for most tools | usually fine |

Always search with `python3 <skill-dir>/scripts/search_code.py --source <src> "<regex>"` (decodes every file, flags files raw grep would miss, `--fold` ignores case and diacritics, `-C N` shows following lines). Run `search_code.py --source <src> --list-encodings` once at bootstrap and record any UTF-16 or code-page files in `APP-OVERVIEW.md`: they are exactly the files most likely to be skipped by tools.

If a type or method truly is undefined after an encoding-safe search, go to section 3. Do not write "defined in a DLL" in an open question until section 3 has been done.

## 2. Enums and constants

Enums hold status lifecycles, role lists, type codes, table names and setting keys. They are referenced by name all over the code and almost never explained, so document them centrally:

1. `python3 <skill-dir>/scripts/enums.py --source <src> --md` lists every enum with members and values (also constants classes).
2. Copy them into the right app-level docs: status enums into `DATA-MODEL.md` (allowed values of the status column) and the lifecycle of the main objects; role/permission enums into `ROLES-MATRIX.md`; setting-key enums into `CONFIG-AND-INTEGRATIONS.md`; everything into `GLOSSARY.md` with the business meaning when known.
3. Value order matters when enums are stored as integers or compared with `<`/`>`: say so in the unit if the code relies on it.
4. Watch for enums whose members are persisted by **name** (`ToString()`) instead of number: renaming a member in the new app then changes stored data. Record which one the legacy uses.

## 3. Assemblies you cannot read as source

`python3 <skill-dir>/scripts/assemblies.py --source <src>` lists every non-framework assembly the projects reference, whether the file exists on disk, and a category:

| Category | Meaning | Action |
|---|---|---|
| third-party (DevExpress, AForge, ...) | vendor library | Not part of the app's logic. Note the capability used (grid, report designer, camera capture) for the tech-stack section. Grid/editor configuration in the forms still holds logic. |
| project-output | built from a project in the solution | The source is in the tree; read it. If the project is missing from the tree, treat as own-code below. |
| unknown/own? | a team-written library | **Its logic may be part of the app.** Find the source; if only a DLL exists, decompile (section 4); if not even the DLL exists, ask the user and record it as a gap. |
| MISSING (HintPath not on disk) | referenced but not handed over | Ask the user for it once, listing all missing ones together. Record each as an Open Question and mark units that depend on it `PARTIAL`. |

Also check `ProjectReference` entries pointing outside the handed-over tree.

## 4. Decompiling an own-code DLL

Only decompile what the user owns or is entitled to analyse, and say that you did so in the docs (a decompiled listing is a reading aid, not source of record). Prefer asking the user for the original source first.

Tools, in order of preference. Check what is installed (`which ilspycmd monodis`, `dotnet --list-sdks`) and ask the user to run an install if none is available; do not install system software silently.

```bash
# ILSpy command line (cross-platform):  dotnet tool install -g ilspycmd
ilspycmd -p -o ./decompiled/<Assembly> path/to/Assembly.dll     # whole project as .cs files
ilspycmd -t Namespace.TypeName path/to/Assembly.dll            # one type to stdout
# Fallbacks: monodis --typedef Assembly.dll   (type list only); dnSpy / dotPeek on Windows
```

Rules for decompiled output:
- Put it **outside** the source tree (e.g. `decompiled/`), never into the user's source.
- Treat names as authoritative but control flow as approximate (compilers inline, lambdas get generated names such as `<>c__DisplayClass`). Check formulas and thresholds by test vectors, not by trusting the decompiler.
- Cite it as `Assembly.dll!Namespace.Type.Method (decompiled)` in `Legacy source`, and set `Confidence: Inferred`.
- Obfuscated assemblies (single-letter names, unreadable strings): stop, record a gap, and ask the user for the source.
- Do not decompile or reproduce licensed third-party libraries; document only how the app uses them.

## 5. What to record when you cannot recover the logic

Never invent behavior. For each unrecoverable dependency:
- Open Question: what is missing, which units are affected, what the user can provide (source, DLL, or a description of the behavior).
- Mark the dependent unit `PARTIAL`; list the call site (`file:method:line`) so the gap is traceable.
- Describe what is observable from the caller's side (parameters in, how the result is used), labelled `Inferred`.
- Add to `CONFIG-AND-INTEGRATIONS.md` under external systems if it is a device or service.
