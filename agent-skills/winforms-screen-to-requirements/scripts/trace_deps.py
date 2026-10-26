#!/usr/bin/env python3
"""Mechanical first pass of dependency tracing for one form/class file.

Lists what to read next: event handlers, forms/controls opened, calls into other classes, SQL and
stored procedures, MessageBox texts, shortcuts/key handling, timers, config/global-state access,
permission checks. Also reports who opens this form. Output is a checklist of leads, not the
analysis itself; read each lead before writing requirements.

Usage: trace_deps.py --source <src> <FormClassOrFile> [--json]
"""
import argparse
import json
import re
from pathlib import Path

from _common import read_text, walk_source

PATTERNS = {
    "handlers": r"(?:void|Sub)\s+(\w+_(?:Click|DoubleClick|Load|Shown|Activated|FormClosing|FormClosed|TextChanged|SelectedIndexChanged|"
                r"ValueChanged|CheckedChanged|Validating|Validated|Leave|Enter|KeyDown|KeyPress|KeyUp|CellClick|CellValueChanged|"
                r"CellValidating|CellEndEdit|CellFormatting|RowEnter|SelectionChanged|Tick|DragDrop|MouseDown|Paint|"
                r"CellContentClick|DataError|UserDeletingRow|Closing))\b",
    "opens_forms": r"(?:new|New)\s+(frm\w+|\w*Form\w*|\w*Dialog\w*)\s*\(",
    "calls_into": r"\b((?:\w+(?:BLL|DAL|Service|Manager|Helper|Repository|Dao|Facade|Logic))|Bll\w+|Dal\w+)\s*(?:\.|\()",
    "sql_text": r"\"((?:SELECT|INSERT|UPDATE|DELETE|EXEC|MERGE)\b[^\"]{0,200})",
    "stored_procs": r"CommandText\s*=\s*\"(\w[\w\.]*)\"|\"(sp_\w+|usp_\w+|proc_\w+|\w+_sp\w*)\"",
    "datasets_adapters": r"\b(\w+TableAdapter|SqlDataAdapter|DataSet|\w+\.xsd|DbContext|ISession|ObjectContext)\b",
    "messages": r"(?:MessageBox\.Show|MsgBox)\s*\(\s*([^;]{0,160})",
    "keys_shortcuts": r"(ProcessCmdKey|KeyPreview|ShortcutKeys|Keys\.\w+|AcceptButton|CancelButton)",
    "timers_threads": r"(Timer|BackgroundWorker|new\s+Thread|Task\.Run|async\s+void)",
    "global_state": r"\b(Session\.\w+|CurrentUser\.\w+|Global\w*\.\w+|Settings\.Default\.\w+|ConfigurationManager\.\w+|Registry\.\w+|Program\.\w+)",
    "permissions": r"(\w*(?:HasPermission|CheckRight|IsInRole|CanEdit|CanDelete|Quyen\w*|Permission\w*|Role\w*)\s*\()",
    "reports_print": r"(ReportViewer|\.rdlc|\.rpt|PrintDocument|PrintPreview|ExportTo\w+|Excel\.\w+|CrystalReport\w*)",
    "computed_fields": r"(\w+\.(?:Text|Value|SelectedValue|Checked|Visible|Enabled|ReadOnly)\s*=\s*[^;\n]{0,100}(?:Add(?:Days|Months|Years)|Math\.\w+|\*|/|DateTime|Parse|Round)[^;\n]{0,60})",
    "datacolumn_expr": r"(\.Expression\s*=\s*\"[^\"]+\"|UnboundExpression|SummaryItem|CustomUnboundColumnData)",
    "external_io": r"(SerialPort|Interop|DllImport|Process\.Start|File\.\w+|WebClient|HttpClient|SmtpClient|Ftp\w+|COM\w*)",
}


def project_classes(src):
    """Names of all classes defined in the source tree (so calls into them can be listed as leads
    whatever naming convention the project uses: NTPObX, MainNTP, KeysListObX, ...)."""
    names = set()
    for f in walk_source(src, {".cs", ".vb"}):
        names.update(re.findall(r"\bclass\s+(\w+)", read_text(f)))
        names.update(re.findall(r"\bClass\s+(\w+)", read_text(f)))
    return names


def resolve(src, target):
    p = Path(target)
    if p.exists():
        stem = p.stem.split(".")[0]
    else:
        stem = target.split(".")[0]
    files = [f for f in walk_source(src, {".cs", ".vb", ".resx"}) if f.stem.split(".")[0].lower() == stem.lower()]
    return stem, files


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("target")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    src = Path(a.source)
    stem, files = resolve(src, a.target)
    if not files:
        raise SystemExit(f"no files found for {a.target}")
    out = {"form": stem, "files": [], "leads": {}, "opened_by": []}
    for f in files:
        out["files"].append({"file": str(f.relative_to(src)), "lines": read_text(f).count("\n") + 1})
    for f in files:
        if f.suffix == ".resx":
            continue
        text = read_text(f)
        for key, pat in PATTERNS.items():
            for m in re.finditer(pat, text, re.I if key in ("sql_text",) else 0):
                val = next((g for g in m.groups() if g), m.group(0)).strip()
                line = text.count("\n", 0, m.start()) + 1
                out["leads"].setdefault(key, {}).setdefault(val, []).append(f"{f.name}:{line}")
    # Calls into project classes (data layer, services, caches), whatever they are named.
    code_files = [(f, read_text(f)) for f in files if f.suffix != ".resx"]
    own = {c for _, tx in code_files for c in re.findall(r"\b[cC]lass\s+(\w+)", tx)}
    classes = project_classes(src) - own - {stem}
    for cls in sorted(classes):
        for f, tx in code_files:
            for m in re.finditer(rf"\b{re.escape(cls)}\s*\.\s*(\w+)", tx):
                out["leads"].setdefault("project_calls", {}).setdefault(f"{cls}.{m.group(1)}", []).append(f"{f.name}:{tx.count(chr(10), 0, m.start()) + 1}")
    # Base class: logic in a parent form belongs to this form too.
    for f in files:
        m = re.search(rf"class\s+{stem}\s*:\s*([\w\.]+)|Class\s+{stem}\s+Inherits\s+([\w\.]+)", read_text(f))
        if m:
            out["base_class"] = (m.group(1) or m.group(2))
            break
    # Who opens this form?
    pat = re.compile(rf"(?:new|New)\s+{stem}\s*\(")
    for f in walk_source(src, {".cs", ".vb"}):
        if f.stem.split(".")[0].lower() == stem.lower():
            continue
        text = read_text(f)
        for m in pat.finditer(text):
            out["opened_by"].append(f"{f.relative_to(src)}:{text.count(chr(10), 0, m.start()) + 1}")
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    print(f"# {stem}  base: {out.get('base_class', '?')}")
    for f in out["files"]:
        print(f"  file {f['file']} ({f['lines']} lines)")
    print("  opened_by:", ", ".join(out["opened_by"]) or "(none found; check menus/reflection)")
    for k, v in out["leads"].items():
        print(f"\n## {k} ({len(v)})")
        for val, locs in sorted(v.items()):
            print(f"  - {val[:110]}  [{', '.join(locs[:3])}{'...' if len(locs) > 3 else ''}]")


if __name__ == "__main__":
    main()
