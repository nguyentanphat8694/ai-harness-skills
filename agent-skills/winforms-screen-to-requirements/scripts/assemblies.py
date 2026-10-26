#!/usr/bin/env python3
"""List every non-framework assembly the projects reference, and whether it is available.

A rewrite spec must not silently skip logic that lives in a binary. For each reference this reports the
project, the HintPath, whether the file exists, and a guess whether it is third-party (DevExpress, AForge...)
or the team's own code. Own-code assemblies that are missing or binary-only need decompiling or the
source from the user (see references/decompile.md). Also scans for ProjectReference targets that are
missing from the handed-over tree.

Usage: assemblies.py --source <src> [--json]
"""
import argparse
import json
import re
from pathlib import Path

FRAMEWORK = re.compile(r"^(System|Microsoft|mscorlib|WindowsBase|Presentation|UIAutomation)", re.I)
KNOWN_THIRD_PARTY = re.compile(r"^(DevExpress|AForge|OpenCV|Telerik|Infragistics|Syncfusion|Newtonsoft|EntityFramework|NLog|log4net|"
                               r"ICSharpCode|Crystal|CrystalDecisions|Interop|AxInterop|Ionic|iTextSharp|EPPlus|ClosedXML|Dapper)", re.I)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    src = Path(a.source)
    projects = {p.stem for p in src.rglob("*.csproj")} | {p.stem for p in src.rglob("*.vbproj")}
    refs, proj_refs = [], []
    for proj in list(src.rglob("*.csproj")) + list(src.rglob("*.vbproj")):
        text = proj.read_text(encoding="utf-8-sig", errors="replace")
        for m in re.finditer(r'<Reference Include="([^",<]+)[^>]*?(?:/>|>(.*?)</Reference>)', text, re.S):
            name, body = m.group(1).strip(), m.group(2) or ""
            if FRAMEWORK.match(name):
                continue
            hp = re.search(r"<HintPath>(.*?)</HintPath>", body)
            path = hp.group(1).replace("\\", "/") if hp else None
            exists = bool(path and (proj.parent / path).resolve().exists())
            third = bool(KNOWN_THIRD_PARTY.match(name))
            refs.append({"project": proj.name, "assembly": name, "hint_path": path, "exists": exists,
                         "category": "third-party" if third else ("project-output" if name in projects else "unknown/own?")})
        for m in re.finditer(r'<ProjectReference Include="([^"]+)"', text):
            target = (proj.parent / m.group(1).replace("\\", "/")).resolve()
            proj_refs.append({"project": proj.name, "references": m.group(1), "exists": target.exists()})
    dlls = sorted(str(p.relative_to(src)) for p in src.rglob("*.dll") if not FRAMEWORK.match(p.name) and "/obj/" not in str(p))
    out = {"references": refs, "project_references": proj_refs, "dlls_in_tree": dlls}
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return
    seen = set()
    print("# Non-framework assemblies (deduplicated)")
    for r in sorted(refs, key=lambda r: (r["category"], r["assembly"])):
        key = (r["assembly"], r["exists"])
        if key in seen:
            continue
        seen.add(key)
        if r["category"] == "third-party" and r["assembly"].startswith("DevExpress"):
            continue  # dozens of DevExpress parts; summarised below
        status = "present" if r["exists"] else ("MISSING" if r["hint_path"] else "GAC/no hint")
        print(f"  [{status:11}] {r['assembly']:38} {r['category']:15} {r['hint_path'] or ''}")
    dx = sorted({r["assembly"] for r in refs if r["assembly"].startswith("DevExpress")})
    if dx:
        print(f"  (+ {len(dx)} DevExpress assemblies, e.g. {dx[0]}; third-party UI: grid/editor config holds logic)")
    print("\n# ProjectReferences")
    for r in proj_refs:
        print(f"  [{'ok' if r['exists'] else 'MISSING'}] {r['project']} -> {r['references']}")
    print(f"\n# DLLs inside the source tree ({len(dlls)})")
    for d in dlls:
        print("  -", d)
    print("\nOwn-code assemblies that are MISSING or present only as DLL: see references/decompile.md")


if __name__ == "__main__":
    main()
