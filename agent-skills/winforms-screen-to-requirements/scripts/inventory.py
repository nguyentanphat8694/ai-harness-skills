#!/usr/bin/env python3
"""One-time (re-runnable) app-wide inventory of a WinForms source tree.

Finds forms, user controls, reports, stored procedures/SQL scripts, timers/background jobs, and
menu items with the form they open. Writes the candidates into STATE.json `inventory` (never
overwrites existing items) and emits a JSON summary. Heuristic: a starting list to be confirmed
by reading, not a guarantee of completeness.

Usage: inventory.py --source <src> --root requirements-docs [--dry-run]
"""
import argparse
import json
import re
from pathlib import Path

from _common import load_state, read_text, save_state, walk_source

CLASS_RE = re.compile(r"(?:partial\s+)?class\s+(\w+)\s*:\s*([\w\.]+)|Class\s+(\w+)\s+Inherits\s+([\w\.]+)", re.I)
FORM_BASES = re.compile(r"(Form|XtraReport|UserControl|XtraForm|XtraUserControl|RadForm|Base\w*Form|frm\w*|uc\w*)$", re.I)
OPEN_FORM_RE = re.compile(r"(?:new\s+|New\s+)(\w+)\s*\([^)]*\)\s*[\.;]?\s*(?:\.?(Show|ShowDialog)\b)?")
MENU_RE = re.compile(r"(\w+)\.(?:Text|Caption)\s*=\s*\"([^\"]+)\"")
CLICK_RE = re.compile(r"(\w+)\.(Click|ItemClick|LinkClicked)\s*\+=\s*(?:new\s+[\w\.]+\()?(?:this\.)?(\w+)")
DECL_RE = re.compile(r"(?:this\.)?(\w+)\s*=\s*new\s+([\w\.]+)\s*\(")
MENU_TYPES = re.compile(r"(Bar\w*Item|BarSubItem|BarButtonItem|BarLargeButtonItem|MenuItem|ToolStrip(?:Menu|Drop\w*|Split\w*)?Item|ToolStripButton|"
                        r"NavBarItem|NavBarGroup|AccordionControlElement|TileItem|BackstageView\w*|RibbonGalleryBarItem|MainMenu|ContextMenu)$")


def control_kind(ctype, event):
    """menu | button | other: from the declared control type, falling back to the event name."""
    if ctype and MENU_TYPES.search(ctype.split(".")[-1]):
        return "menu"
    if event == "ItemClick":  # DevExpress bar items raise ItemClick; ordinary buttons raise Click
        return "menu"
    if ctype and re.search(r"(Button|CheckBox|Label|PictureBox|HyperLink)", ctype.split(".")[-1]):
        return "button"
    return "other"


SP_RE = re.compile(r"CREATE\s+(?:OR\s+ALTER\s+)?(PROC(?:EDURE)?|FUNCTION|TRIGGER|VIEW)\s+([\w\.\[\]]+)", re.I)
TIMER_RE = re.compile(r"\b(System\.Windows\.Forms\.Timer|System\.Timers\.Timer|BackgroundWorker|new\s+Thread|Task\.Run)\b")


def slug(name):
    return re.sub(r"[^A-Za-z0-9]", "", name)


def body_at(text, start):
    """Text of a {...} block whose opening brace ends just before `start` (brace matching)."""
    depth, i = 1, start
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[start:i]


def strip_comments(t):
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", t, flags=re.S)


def reachable_body(name, bodies, depth=3):
    """Handler body plus the bodies of same-form methods it calls (handlers often delegate to
    helpers like LoadControlX() that do the `new Form()`). Follows calls up to `depth` levels."""
    seen, frontier, out = set(), [name], []
    for _ in range(depth + 1):
        nxt = []
        for n in frontier:
            if n in seen or n not in bodies:
                continue
            seen.add(n)
            out.append(strip_comments(bodies[n]))
            nxt += [c for c in re.findall(r"\b(\w+)\s*\(", bodies[n]) if c in bodies and c not in seen]
        frontier = nxt
    return "\n".join(out)


def callers_of(src, items):
    """class -> {"files": [...], "kinds": [...]} for every OTHER form/file that mentions it.

    Deliberately broad so "orphan" means "never mentioned anywhere else": instantiation (`new X`), static
    use (`X.Foo`), inheritance (`: X`), type use (field/param/generic/typeof/cast), and string mentions
    (reflection or config, e.g. "frmX"). Comments are stripped first. Own files (X.cs, X.Designer.cs,
    X.resx) are excluded.
    """
    names = set(items)
    refs = {n: {} for n in names}
    for f in walk_source(src, {".cs", ".vb", ".resx", ".config", ".settings"}):
        own = f.stem.split(".")[0]
        text = re.sub(r"//[^\n]*|/\*.*?\*/", "", read_text(f), flags=re.S) if f.suffix in (".cs", ".vb") else read_text(f)
        for n in names:
            if n == own or n not in text:
                continue
            for kind, pat in (("new", rf"\bnew\s+{n}\b"), ("inherits", rf":\s*{n}\b|Inherits\s+{n}\b"),
                              ("static", rf"\b{n}\s*\."), ("type", rf"\b{n}\s+\w+\s*[;=,)]|<\s*{n}\s*>|typeof\s*\(\s*{n}|\(\s*{n}\s*\)"),
                              ("string", rf'"[^"\n]*\b{n}\b[^"\n]*"')):
                if re.search(pat, text):
                    refs[n].setdefault(own, set()).add(kind)
    return {n: [{"file": f, "kinds": sorted(k)} for f, k in sorted(v.items())] for n, v in refs.items()}


def entry_points(src, items):
    """Forms started from Main / Program: Application.Run(new X()) and similar."""
    out = set()
    for f in walk_source(src, {".cs", ".vb"}):
        for m in re.finditer(r"Application\.Run\s*\(\s*(?:new\s+)?(\w+)", read_text(f)):
            if m.group(1) in items:
                out.add(m.group(1))
    return sorted(out)


def scan(source):
    src = Path(source)
    items, menus, jobs = {}, [], []
    for f in walk_source(src):
        rel = str(f.relative_to(src))
        ext = f.suffix.lower()
        text = read_text(f)
        if ext in (".cs", ".vb") and not f.name.lower().endswith((".designer.cs", ".designer.vb")):
            for m in CLASS_RE.finditer(text):
                name, base = (m.group(1) or m.group(3)), (m.group(2) or m.group(4))
                if FORM_BASES.search(base.split(".")[-1]):
                    bl = base.lower()
                    kind = "RPT" if "report" in bl else "CMP" if "control" in bl or bl.startswith("uc") else "SCR"
                    entry = items.setdefault(name, {"type": kind, "class": name, "base": base, "files": [], "caption": ""})
                    entry["files"].append(rel)
                    dz = f.with_name(f.stem + (".Designer" + ext))
                    if dz.exists():
                        entry["files"].append(str(dz.relative_to(src)))
                        cap = re.search(r"this\.Text\s*=\s*\"([^\"]*)\"|Me\.Text\s*=\s*\"([^\"]*)\"", read_text(dz))
                        if cap:
                            entry["caption"] = cap.group(1) or cap.group(2)
            if TIMER_RE.search(text):
                jobs.append({"file": rel, "hint": sorted(set(TIMER_RE.findall(text)))})
        if ext in (".rdlc", ".rpt"):
            items[f.stem] = {"type": "RPT", "class": f.stem, "files": [rel], "caption": ""}
        if ext == ".sql":
            for kind, nm in SP_RE.findall(text):
                nm = nm.replace("[", "").replace("]", "")
                items[nm] = {"type": "DB", "class": nm, "kind": kind.upper(), "files": [rel], "caption": ""}
    # Menu items: caption + click handler + forms opened in that handler. Wiring (Designer) and
    # handler bodies (code-behind) are often in different files, so collect project-wide first.
    # Scope by form: control names repeat across forms, so match only within Foo.cs + Foo.Designer.cs.
    groups = {}
    for f in walk_source(src, {".cs", ".vb"}):
        groups.setdefault(str(f.parent / f.stem.split(".")[0]), []).append(f)
    seen = set()
    unwired, buttons = [], []
    for files in groups.values():
        caps, wires, bodies, ctypes = {}, [], {}, {}
        for f in files:
            text = read_text(f)
            caps.update({m.group(1): m.group(2) for m in MENU_RE.finditer(text)})
            wires += [(c, ev, h) for c, ev, h in CLICK_RE.findall(text)]
            ctypes.update({m.group(1): m.group(2) for m in DECL_RE.finditer(text)})
            for m in re.finditer(r"(?:void|Sub|bool|Form|\w+Form)\s+(\w+)\s*\([^)]*\)\s*\{", text):
                bodies.setdefault(m.group(1), body_at(text, m.end()))
        wired = {h for _, _, h in wires}
        for h, body in bodies.items():
            if h.endswith(("_Click", "_ItemClick")) and h not in wired:
                opened = sorted({o[0] for o in OPEN_FORM_RE.findall(reachable_body(h, bodies))} & set(items))
                if opened:
                    unwired.append({"in_form": files[0].stem.split(".")[0], "handler": h, "opens": opened})
        for ctl, event, handler in wires:
            if handler not in bodies:
                continue
            opened = sorted({o[0] for o in OPEN_FORM_RE.findall(reachable_body(handler, bodies))} & set(items))
            if not opened:
                continue
            form = files[0].stem.split(".")[0]
            kind = control_kind(ctypes.get(ctl), event)
            entry = {"caption": " ".join(caps.get(ctl, ctl).split()), "control": ctl, "control_type": ctypes.get(ctl, "?"),
                     "handler": handler, "opens": opened, "in_form": form}
            key = (form, ctl)
            if key in seen:
                continue
            seen.add(key)
            # Real menu items need a caption; buttons are screen-to-screen links, kept separately.
            (menus if kind == "menu" and ctl in caps else buttons).append(entry)
    return items, menus, jobs, unwired, callers_of(src, items), entry_points(src, items), buttons


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--root", default="requirements-docs")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    items, menus, jobs, unwired, callers, entries, buttons = scan(a.source)
    summary = {"counts": {}, "menus": menus, "jobs": jobs, "button_links": buttons, "unwired_handlers": unwired, "entry_points": entries}
    for it in items.values():
        summary["counts"][it["type"]] = summary["counts"].get(it["type"], 0) + 1
    if not a.dry_run:
        st = load_state(a.root)
        for name, it in items.items():
            it["files"] = sorted(set(it["files"]))
            st["inventory"].setdefault(f"{it['type']}:{name}", {**it, "unit": None})
        st["menus"] = menus
        st["button_links"] = buttons
        st["unwired_handlers"] = unwired
        st["callers"] = callers
        st["entry_points"] = entries
        save_state(a.root, st)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
