#!/usr/bin/env python3
"""Assemble SRS.md from the generated docs. Stitches existing content and lists gaps; does not invent.

Blocks between <!-- manual:start --> and <!-- manual:end --> in an existing SRS.md are preserved.

Usage: build_srs.py --root requirements-docs
"""
import argparse
import re
from pathlib import Path

from _common import load_state, today

SECTIONS = [("1. Application overview", "APP-OVERVIEW.md"), ("2. Navigation and screen flows", "NAVIGATION.md"),
            ("3. Roles and permissions", "ROLES-MATRIX.md"), ("4. Data model", "DATA-MODEL.md"),
            ("5. Configuration and integrations", "CONFIG-AND-INTEGRATIONS.md"), ("6. End-to-end workflows", "WORKFLOWS.md"),
            ("7. Characteristic business functions", "FUNCTIONS.md"), ("8. Improvements", "IMPROVEMENTS.md"),
            ("9. Open questions", "OPEN-QUESTIONS.md"), ("10. Glossary", "GLOSSARY.md")]


def demote(text, by=2):
    return re.sub(r"^(#+)", lambda m: "#" * min(6, len(m.group(1)) + by), text, flags=re.M)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="requirements-docs")
    a = ap.parse_args()
    root = Path(a.root)
    st = load_state(root)
    out = root / "SRS.md"
    manual = re.findall(r"<!-- manual:start -->.*?<!-- manual:end -->", out.read_text(encoding="utf-8"), re.S) if out.exists() else []
    gaps = []
    lines = [f"# Software Requirements Specification", "", f"_Assembled {today()} from requirements-docs. Rebuild with scripts/build_srs.py._", ""]
    lines += manual[:1] or ["<!-- manual:start -->", "(Add business context, decisions and legacy differences here.)", "<!-- manual:end -->"]
    for title, fn in SECTIONS:
        f = root / fn
        lines += ["", f"## {title}", ""]
        if f.exists() and f.read_text(encoding="utf-8").strip():
            lines.append(demote(re.sub(r"\A# .*\n", "", f.read_text(encoding="utf-8"))))
        else:
            lines.append(f"_Missing: {fn}_")
            gaps.append(f"{fn} missing or empty")
    lines += ["", "## 11. Requirements by module", ""]
    mods = {}
    for uid, u in sorted(st["units"].items()):
        mods.setdefault(uid.split("-")[1], []).append((uid, u))
    for m, units in mods.items():
        lines += [f"### Module {m}", ""]
        mf = root / "modules" / m / "MODULE.md"
        if mf.exists():
            lines += [f"See [{m} module description](modules/{m}/MODULE.md).", ""]
        lines += ["| Unit | Status | Document |", "|---|---|---|"]
        for uid, u in units:
            lines.append(f"| {uid} | {u['status']} | [{uid}.md]({u['doc']}) |")
            if u["status"] != "DONE":
                gaps.append(f"{uid} is {u['status']}")
        lines.append("")
    for k, i in st.get("inventory", {}).items():
        if not i.get("unit") and not i.get("orphan"):
            gaps.append(f"inventory item {k} has no unit")
    lines += ["## 12. Known gaps at assembly time", ""] + ([f"- {g}" for g in gaps] or ["- none"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}; {len(gaps)} gap(s)")


if __name__ == "__main__":
    main()
