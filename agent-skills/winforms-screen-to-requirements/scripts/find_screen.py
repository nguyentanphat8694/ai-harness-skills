#!/usr/bin/env python3
"""Locate the form(s) behind a screen the user points at (caption, label/button text, class, menu).

Feed it every distinct text you can read off the screenshot (title bar, labels, button captions,
column headers, menu path). Candidates are ranked by how many of the strings they contain, so a
form matching 6 of 8 strings beats one matching 1. Diacritic- and case-insensitive.

Usage: find_screen.py --source <src> "Khám thai" "Ngày kinh cuối" "Lưu" [--top 5]
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from _common import fold, read_text, walk_source

STR_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("texts", nargs="+")
    a = ap.parse_args()
    needles = [fold(t) for t in a.texts]
    src = Path(a.source)
    hits = defaultdict(lambda: {"matched": set(), "files": set()})
    for f in walk_source(src, {".cs", ".vb", ".resx"}):
        text = read_text(f)
        literals = [fold(s) for s in STR_RE.findall(text)] if f.suffix != ".resx" else [fold(text)]
        # Group by form: Foo.cs, Foo.Designer.cs, Foo.resx all belong to "Foo".
        key = re.sub(r"\.(designer|[a-z]{2}(-[a-z]+)?)$", "", f.stem, flags=re.I)
        for n in needles:
            if any(n and n in lit for lit in literals) or fold(key) == n.replace(" ", ""):
                hits[key]["matched"].add(n)
                hits[key]["files"].add(str(f.relative_to(src)))
    ranked = sorted(hits.items(), key=lambda kv: -len(kv[1]["matched"]))[: a.top]
    print(json.dumps([{"form": k, "score": f"{len(v['matched'])}/{len(needles)}", "missing": [n for n in needles if n not in v["matched"]],
                       "files": sorted(v["files"])} for k, v in ranked], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
