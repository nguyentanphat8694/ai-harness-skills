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
FORM_BASES = re.compile(r"(Form|UserControl|XtraForm|XtraUserControl|RadForm|Base\w*Form|frm\w*|uc\w*)$", re.I)
OPEN_FORM_RE = re.compile(r"(?:new\s+|New\s+)(\w+)\s*\([^)]*\)\s*[\.;]?\s*(?:\.?(Show|ShowDialog)\b)?")
MENU_RE = re.compile(r"(\w+)\.(?:Text|Caption)\s*=\s*\"([^\"]+)\"")
CLICK_RE = re.compile(r"(\w+)\.(?:Click|ItemClick|LinkClicked)\s*\+=\s*(?:new\s+[\w\.]+\()?(?:this\.)?(\w+)")
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
            out.append(bodies[n])
            nxt += [c for c in re.findall(r"\b(\w+)\s*\(", bodies[n]) if c in bodies and c not in seen]
        frontier = nxt
    return "\n".join(out)


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
                    kind = "CMP" if "control" in base.lower() or base.lower().startswith("uc") else "SCR"
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
    unwired = []
    for files in groups.values():
        caps, wires, bodies = {}, [], {}
        for f in files:
            text = read_text(f)
            caps.update({m.group(1): m.group(2) for m in MENU_RE.finditer(text)})
            wires += CLICK_RE.findall(text)
            for m in re.finditer(r"(?:void|Sub|bool|Form|\w+Form)\s+(\w+)\s*\([^)]*\)\s*\{", text):
                bodies.setdefault(m.group(1), body_at(text, m.end()))
        wired = {h for _, h in wires}
        for h, body in bodies.items():
            if h.endswith(("_Click", "_ItemClick")) and h not in wired:
                opened = sorted({o[0] for o in OPEN_FORM_RE.findall(reachable_body(h, bodies))} & set(items))
                if opened:
                    unwired.append({"in_form": files[0].stem.split(".")[0], "handler": h, "opens": opened})
        for ctl, handler in wires:
            if ctl in caps and handler in bodies:
                opened = sorted({o[0] for o in OPEN_FORM_RE.findall(reachable_body(handler, bodies))} & set(items))
                key = (files[0].stem.split(".")[0], ctl)
                if opened and key not in seen:
                    seen.add(key)
                    menus.append({"caption": " ".join(caps[ctl].split()), "control": ctl, "handler": handler,
                                  "opens": opened, "in_form": key[0]})
    return items, menus, jobs, unwired


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--root", default="requirements-docs")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    items, menus, jobs, unwired = scan(a.source)
    summary = {"counts": {}, "menus": menus, "jobs": jobs, "unwired_handlers": unwired}
    for it in items.values():
        summary["counts"][it["type"]] = summary["counts"].get(it["type"], 0) + 1
    if not a.dry_run:
        st = load_state(a.root)
        for name, it in items.items():
            st["inventory"].setdefault(f"{it['type']}:{name}", {**it, "unit": None})
        st["menus"] = menus
        st["unwired_handlers"] = unwired
        save_state(a.root, st)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
