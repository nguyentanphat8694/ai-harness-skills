#!/usr/bin/env python3
"""Mechanical part of the "nothing missed" gate for a unit doc.

Checks: (1) every event handler found in the form source appears in the unit doc's Coverage table;
(2) every MessageBox/MsgBox call is represented in the Messages section (count compare);
(3) every REQ/BR/FN has an Assessment field and non-OK ones link an IMP;
(4) no duplicate IDs; no REQ sharing the same legacy source; (5) every FN has >=3 test vectors lines.
Exit code 1 when anything fails, so it can gate `state.py commit`.

Usage: check_unit.py --source <src> --root requirements-docs <UNIT-ID> <FormClass>
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from _common import load_state, read_text
from trace_deps import PATTERNS, resolve


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--root", default="requirements-docs")
    ap.add_argument("unit")
    ap.add_argument("form", nargs="?", help="form class name (omit for units without a form)")
    a = ap.parse_args()
    st = load_state(a.root)
    u = st["units"].get(a.unit) or sys.exit(f"unknown unit {a.unit}")
    doc = Path(a.root) / u["doc"]
    text = doc.read_text(encoding="utf-8")
    fails, warns = [], []

    if a.form:
        _, files = resolve(Path(a.source), a.form)
        code = "\n".join(read_text(f) for f in files if f.suffix != ".resx")
        handlers = set(re.findall(PATTERNS["handlers"], code))
        missing = sorted(h for h in handlers if h not in text)
        if missing:
            fails.append(f"handlers not in Coverage table ({len(missing)}): {', '.join(missing[:15])}")
        msgs = len(re.findall(r"MessageBox\.Show|MsgBox", code))
        sec10 = re.search(r"##\s*10\..*?(?=\n##\s*11\.)", text, re.S)
        rows = len([l for l in (sec10.group(0).splitlines() if sec10 else []) if l.startswith("|") and not re.match(r"\|\s*(-|Message)", l)])
        if msgs > rows:
            fails.append(f"{msgs} MessageBox calls in source but only {rows} rows in Messages section")

    ids = re.findall(r"^#{2,4}\s*((?:REQ|FN|IMP)-[A-Za-z0-9-]+)", text, re.M)
    for k, n in Counter(ids).items():
        if n > 1:
            fails.append(f"duplicate ID {k}")
    blocks = re.split(r"^#{3,4}\s+(?=(?:REQ|FN)-)", text, flags=re.M)[1:]
    srcs = Counter()
    for b in blocks:
        head = b.splitlines()[0]
        m = re.search(r"\*\*(?:Assessment)\*\*:\s*(\S+)(.*)", b)
        if not m:
            fails.append(f"{head[:40]}: missing Assessment")
        elif m.group(1).upper().startswith(("SUSPECT", "WRONG", "MISSING", "OUTDATED")) and "IMP-" not in m.group(2):
            fails.append(f"{head[:40]}: non-OK assessment without IMP link")
        s = re.search(r"\*\*Legacy source\*\*:\s*(.+)", b)
        if s and head.startswith("REQ-") and "User request" not in s.group(1):
            srcs[s.group(1).strip()] += 1
        if head.startswith("FN-"):
            tv = re.search(r"\*\*Test vectors?\*\*.*?(?=\n- \*\*|\Z)", b, re.S)
            if not tv or len(re.findall(r"->|→", tv.group(0))) < 3:
                fails.append(f"{head[:40]}: fewer than 3 test vectors")
    for s, n in srcs.items():
        if n > 1:
            warns.append(f"{n} REQs share legacy source '{s[:60]}' (merge or confirm distinct)")
    for sec in ("2.", "9.", "10.", "11.", "12."):
        if not re.search(rf"##\s*{re.escape(sec)}", text):
            fails.append(f"section {sec} missing")
    for w in warns:
        print("WARN", w)
    for f in fails:
        print("FAIL", f)
    print("OK: mechanical gate passed" if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
