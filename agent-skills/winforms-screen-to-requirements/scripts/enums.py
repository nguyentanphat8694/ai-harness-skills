#!/usr/bin/env python3
"""Extract every enum (name, members, explicit values, [Flags]) and constants class from the source.

Enums are where status lifecycles, role lists, type codes and table names live, and they are referenced
by name all over the code. Run this once at bootstrap and again when STATE reports source drift, then use
the result in GLOSSARY.md, DATA-MODEL.md (status columns) and ROLES-MATRIX.md.

Handles UTF-16 and legacy code pages (see search_code.py). Output is JSON, or a Markdown table with --md.

Usage: enums.py --source <src> [--md] [--name etrangthai]
"""
import argparse
import json
import re
from pathlib import Path

from _common import read_text, walk_source

ENUM_RE = re.compile(r"((?:\[[^\]]*\]\s*)*)\b(?:public|internal|private|protected)?\s*enum\s+(\w+)\s*(?::\s*(\w+))?\s*\{(.*?)\n?\s*\}", re.S)
VB_ENUM_RE = re.compile(r"\bEnum\s+(\w+)\s*(.*?)\bEnd\s+Enum", re.S | re.I)
CONST_CLASS_RE = re.compile(r"(?:static\s+)?class\s+(\w+)\s*\{((?:\s*(?:public\s+)?(?:const|static\s+readonly)\s+[^;]+;|\s*//[^\n]*)+)\s*\}", re.S)


def strip_comments(t):
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", t, flags=re.S)


def parse_members(body):
    members, nxt = [], 0
    for raw in strip_comments(body).replace("\n", " ").split(","):
        raw = re.sub(r"\[[^\]]*\]", "", raw).strip()
        if not raw:
            continue
        m = re.match(r"(\w+)\s*(?:=\s*(.+))?$", raw)
        if not m:
            continue
        name, val = m.group(1), m.group(2)
        if val is not None:
            try:
                nxt = int(val.strip(), 0)
            except ValueError:
                nxt = None  # expression / reference to another member
        members.append({"name": name, "value": nxt if nxt is not None else val.strip()})
        if isinstance(nxt, int):
            nxt += 1
    return members


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--name", help="only this enum (case-insensitive)")
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    src = Path(a.source)
    found = []
    for f in walk_source(src, {".cs", ".vb"}):
        text = read_text(f)
        rel = str(f.relative_to(src))
        for attrs, name, base, body in ENUM_RE.findall(text):
            found.append({"name": name, "kind": "enum", "flags": "Flags" in attrs, "base": base or "int",
                          "members": parse_members(body), "file": rel})
        for name, body in VB_ENUM_RE.findall(text):
            found.append({"name": name, "kind": "enum", "flags": False, "base": "int",
                          "members": parse_members(re.sub(r"\n", ",", body)), "file": rel})
        for name, body in CONST_CLASS_RE.findall(text):
            consts = re.findall(r"(?:const|static\s+readonly)\s+\w+\s+(\w+)\s*=\s*([^;]+);", body)
            if consts:
                found.append({"name": name, "kind": "constants", "flags": False, "base": "",
                              "members": [{"name": n, "value": v.strip()} for n, v in consts], "file": rel})
    if a.name:
        found = [e for e in found if e["name"].lower() == a.name.lower()]
    if not a.md:
        print(json.dumps(found, indent=2, ensure_ascii=False))
        return
    print("| Enum / constants | Members (value) | Defined in |\n|---|---|---|")
    for e in sorted(found, key=lambda e: e["name"].lower()):
        mem = ", ".join(f"{m['name']}={m['value']}" for m in e["members"])
        print(f"| `{e['name']}`{' [Flags]' if e['flags'] else ''} | {mem} | {e['file']} |")


if __name__ == "__main__":
    main()
