#!/usr/bin/env python3
"""Encoding-safe code search. Use this instead of raw `grep` on legacy source.

Legacy .NET projects often contain UTF-16 (BOM) or legacy-code-page files (Windows-1258/1252). Raw grep
reads bytes, so a UTF-16 file never matches ASCII text, and a Vietnamese string saved in cp1258 never
matches its UTF-8 form. A search that silently returns nothing is how definitions get "lost".

This script decodes every file correctly, matches case-insensitively and diacritic-insensitively when
asked, and always reports which files could not be decoded cleanly.

Usage:
  search_code.py --source <src> "etrangthai"                       # regex, all code files
  search_code.py --source <src> "enum\\s+etrangthai" --context 12   # show lines after the match too
  search_code.py --source <src> "khám thai" --fold --ext .cs .resx  # ignore case + diacritics
  search_code.py --source <src> --list-encodings                    # which files are not plain UTF-8
"""
import argparse
import re
import sys
from pathlib import Path

from _common import SOURCE_EXTS, detect_encoding, fold, read_text, walk_source


HARD = {"utf-16", "legacy-codepage"}  # encodings that break byte-based tools


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("pattern", nargs="?")
    ap.add_argument("--ext", nargs="*", help="extensions to search (default: all code/config/resource types)")
    ap.add_argument("--fold", action="store_true", help="case- and diacritic-insensitive literal/regex match")
    ap.add_argument("--context", "-C", type=int, default=0, help="lines of context after each match")
    ap.add_argument("--max", type=int, default=200, help="max matches to print")
    ap.add_argument("--files-only", "-l", action="store_true")
    ap.add_argument("--list-encodings", action="store_true",
                    help="list files that raw grep cannot read correctly (UTF-16, legacy code page)")
    ap.add_argument("--all-encodings", action="store_true", help="with --list-encodings: also list UTF-8 BOM / ASCII")
    a = ap.parse_args()
    src = Path(a.source)
    exts = {e if e.startswith(".") else "." + e for e in a.ext} if a.ext else SOURCE_EXTS

    if a.list_encodings:
        for f in walk_source(src, exts):
            enc = detect_encoding(f)
            if enc in HARD or (a.all_encodings and enc != "utf-8"):
                print(f"{enc:16} {f.relative_to(src)}")
        return
    if not a.pattern:
        ap.error("pattern is required")

    rx = re.compile(fold(a.pattern) if a.fold else a.pattern, 0 if a.fold else re.I)
    shown = hits = 0
    odd = []
    for f in walk_source(src, exts):
        enc = detect_encoding(f)
        if enc in HARD:
            odd.append((enc, f))
        lines = read_text(f).splitlines()
        hay = [fold(l) for l in lines] if a.fold else lines
        matched = [i for i, l in enumerate(hay) if rx.search(l)]
        if not matched:
            continue
        hits += len(matched)
        rel = f.relative_to(src)
        if a.files_only:
            print(rel)
            continue
        for i in matched:
            if shown >= a.max:
                break
            print(f"{rel}:{i + 1}: {lines[i].strip()[:200]}")
            for j in range(i + 1, min(i + 1 + a.context, len(lines))):
                print(f"{rel}:{j + 1}  {lines[j].rstrip()[:200]}")
            shown += 1
    print(f"-- {hits} match(es)" + (f", showing first {a.max}" if hits > a.max else ""), file=sys.stderr)
    if odd:
        print(f"-- note: {len(odd)} file(s) would be invisible to raw grep (decoded correctly here): "
              + ", ".join(f"{p.name}[{e}]" for e, p in odd[:6]) + (" ..." if len(odd) > 6 else ""), file=sys.stderr)


if __name__ == "__main__":
    main()
