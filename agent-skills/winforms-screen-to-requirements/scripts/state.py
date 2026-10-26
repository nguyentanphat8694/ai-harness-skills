#!/usr/bin/env python3
"""Manage STATE.json for the requirements docs: init, check, ids, register, commit, index.

Run `state.py <command> --help` for options. All commands take --root (default: requirements-docs).
STATE.json is the single source of truth for status, rev, hashes and ID counters.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from _common import ID_RE, file_hash, load_state, save_state, today

STATUSES = ["PENDING", "IN_PROGRESS", "PARTIAL", "DONE", "STALE"]


def cmd_init(a):
    root = Path(a.root)
    root.mkdir(parents=True, exist_ok=True)
    if (root / "STATE.json").exists():
        sys.exit("STATE.json already exists; refusing to overwrite. Use `check` instead.")
    state = {
        "schema": 2, "root": str(root), "source_root": a.source, "hash_method": "sha1-lf",
        "doc_language": a.lang, "counters": {}, "inventory": {}, "units": {}, "queue": [], "log": [],
    }
    # Adopt pre-existing docs: counters = highest number seen per ID prefix.
    for md in root.rglob("*.md"):
        for m in ID_RE.finditer(md.read_text(encoding="utf-8", errors="replace")):
            key, n = m.group(1).rsplit("-", 1)
            state["counters"][key] = max(state["counters"].get(key, 0), int(n))
    save_state(root, state)
    print(f"initialised {root}/STATE.json (counters adopted from {len(state['counters'])} prefixes)")


def cmd_check(a):
    """Session start: doc hash mismatches, source drift, IN_PROGRESS units."""
    st = load_state(a.root)
    root, src = Path(a.root), Path(st.get("source_root") or ".")
    problems = {"doc_edited_outside_skill": [], "missing_doc": [], "source_drift": [], "in_progress": [], "stale_dependents": {}}
    for uid, u in st["units"].items():
        if u["status"] == "IN_PROGRESS":
            problems["in_progress"].append((uid, u.get("checkpoint", "")))
        if u["status"] == "PENDING":
            continue
        doc = root / u["doc"]
        if not doc.exists():
            problems["missing_doc"].append(uid)
        elif u.get("doc_hash") and file_hash(doc) != u["doc_hash"]:
            problems["doc_edited_outside_skill"].append(uid)
        for rel, h in u.get("sources", {}).items():
            p = src / rel
            if not p.exists() or file_hash(p) != h:
                problems["source_drift"].append((uid, rel, "deleted" if not p.exists() else "changed"))
    drifted = {x[0] for x in problems["source_drift"]}
    for uid in drifted:
        if a.mark_stale and st["units"][uid]["status"] == "DONE":
            st["units"][uid]["status"] = "STALE"
        problems["stale_dependents"][uid] = [d for d, u in st["units"].items() if uid in u.get("deps", [])]
    if a.mark_stale:
        save_state(a.root, st)
    print(json.dumps(problems, indent=2, ensure_ascii=False))


def cmd_next_id(a):
    """Allocate IDs. Prefix examples: REQ-SAN-KhamThai, BR-SAN, FN-SAN, IMP-SAN, Q."""
    st = load_state(a.root)
    start = st["counters"].get(a.prefix, 0)
    st["counters"][a.prefix] = start + a.count
    save_state(a.root, st)
    width = 3
    for i in range(start + 1, start + a.count + 1):
        print(f"{a.prefix}-{i:0{width}d}")


def cmd_register(a):
    """Create or update a unit entry. Also dedups by alias/source (never two units for one form)."""
    st = load_state(a.root)
    uid = a.unit
    for other, u in st["units"].items():
        if other != uid and (set(map(str.lower, a.alias or [])) & set(map(str.lower, u.get("aliases", [])))):
            sys.exit(f"alias already belongs to {other}; reuse that unit instead of creating {uid}")
    u = st["units"].setdefault(uid, {"status": "PENDING", "rev": 0, "sources": {}, "aliases": [], "deps": []})
    mod = uid.split("-")[1]
    u["doc"] = f"modules/{mod}/units/{uid}.md"
    u["aliases"] = sorted(set(u["aliases"]) | set(a.alias or []))
    u["deps"] = sorted(set(u["deps"]) | set(a.dep or []))
    for rel in a.source or []:
        u["sources"].setdefault(rel, "")
    if a.inventory:
        inv = st["inventory"].get(a.inventory)
        if inv is None:
            sys.exit(f"inventory item {a.inventory} not found")
        inv["unit"] = uid
    for d in a.dep or []:
        if d not in st["units"]:
            st["units"][d] = {"status": "PENDING", "rev": 0, "sources": {}, "aliases": [], "deps": []}
            mod_d = d.split("-")[1]
            st["units"][d]["doc"] = f"modules/{mod_d}/units/{d}.md"
    save_state(a.root, st)
    print(f"registered {uid}")


def cmd_set(a):
    """Set status/checkpoint (use IN_PROGRESS + checkpoint after each completed part)."""
    st = load_state(a.root)
    u = st["units"].get(a.unit) or sys.exit(f"unknown unit {a.unit}")
    u["status"] = a.status
    if a.checkpoint is not None:
        u["checkpoint"] = a.checkpoint
    save_state(a.root, st)


def cmd_commit(a):
    """Final step for a unit: refresh source/doc hashes, bump rev, set status, append log."""
    st = load_state(a.root)
    root, src = Path(a.root), Path(st.get("source_root") or ".")
    u = st["units"].get(a.unit) or sys.exit(f"unknown unit {a.unit}")
    doc = root / u["doc"]
    if not doc.exists():
        sys.exit(f"doc {doc} does not exist; write the unit file first")
    for rel in list(u["sources"]):
        p = src / rel
        u["sources"][rel] = file_hash(p) if p.exists() else ""
    u.update(doc_hash=file_hash(doc), rev=u["rev"] + 1, status=a.status, analyzed_at=today())
    u.pop("checkpoint", None)
    st["log"].append({"date": today(), "action": a.action, "units": [a.unit], "note": a.note or ""})
    save_state(a.root, st)
    print(f"{a.unit}: {a.status} rev {u['rev']}")


def cmd_log(a):
    st = load_state(a.root)
    st["log"].append({"date": today(), "action": a.action, "units": a.units or [], "note": a.note or ""})
    save_state(a.root, st)


def count_in_doc(path, prefix):
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    # IDs appear as headings (REQ/FN/IMP) or as the first cell of a table row (BR).
    return len(set(re.findall(rf"^(?:#+\s*|\|\s*)({prefix}-[A-Za-z0-9-]*\d{{3}})", text, re.M)))


def open_questions(root):
    f = Path(root) / "OPEN-QUESTIONS.md"
    if not f.exists():
        return {}
    out = {}
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[0].startswith("Q-") and cells[4].upper() == "OPEN":
            out[cells[1]] = out.get(cells[1], 0) + 1
    return out


def cmd_index(a):
    """Rebuild INDEX.md from STATE.json and unit docs. Never hand-edit INDEX.md."""
    st = load_state(a.root)
    root = Path(a.root)
    oq = open_questions(root)
    mods = {}
    rows = []
    for uid, u in sorted(st["units"].items()):
        typ, mod, *_ = uid.split("-")
        mods.setdefault(mod, []).append(u["status"])
        d = root / u["doc"]
        rows.append(f"| {uid} | {typ} | {mod} | {u['status']} | {count_in_doc(d, 'REQ')} | {count_in_doc(d, 'BR')} | "
                    f"{count_in_doc(d, 'FN')} | {count_in_doc(d, 'IMP')} | {oq.get(uid, 0)} | {u.get('analyzed_at', '')} |")
    inv = st.get("inventory", {})
    done = sum(1 for i in inv.values() if i.get("unit") and st["units"].get(i["unit"], {}).get("status") == "DONE")
    lines = ["# INDEX", "", "(Generated from STATE.json and the unit docs. Do not edit by hand.)", "",
             f"**Coverage**: {done}/{len(inv)} inventory items DONE" + (f" ({100 * done // len(inv)}%)" if inv else ""), "",
             "## Modules", "| Module | Units | DONE | PARTIAL | PENDING |", "|---|---|---|---|---|"]
    for m, sts in sorted(mods.items()):
        lines.append(f"| {m} | {len(sts)} | {sts.count('DONE')} | {sts.count('PARTIAL')} | {sts.count('PENDING')} |")
    lines += ["", "## Units", "| Unit | Type | Module | Status | #REQ | #BR | #FN | #IMP | Open Q | Updated |",
              "|---|---|---|---|---|---|---|---|---|---|", *rows, "", "## Dependencies (unit -> unit)"]
    for uid, u in sorted(st["units"].items()):
        if u.get("deps"):
            lines.append(f"- {uid} -> {', '.join(u['deps'])}")
    lines += ["", "## Queue (discovered, not yet read)"] + [f"- {q}" for q in st.get("queue", [])]
    (root / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {root / 'INDEX.md'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="requirements-docs")
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("init"); p.add_argument("--source", required=True); p.add_argument("--lang", default="en"); p.set_defaults(f=cmd_init)
    p = sp.add_parser("check"); p.add_argument("--mark-stale", action="store_true"); p.set_defaults(f=cmd_check)
    p = sp.add_parser("next-id"); p.add_argument("prefix"); p.add_argument("--count", type=int, default=1); p.set_defaults(f=cmd_next_id)
    p = sp.add_parser("register"); p.add_argument("unit")
    p.add_argument("--source", action="append"); p.add_argument("--alias", action="append"); p.add_argument("--dep", action="append")
    p.add_argument("--inventory"); p.set_defaults(f=cmd_register)
    p = sp.add_parser("set"); p.add_argument("unit"); p.add_argument("status", choices=STATUSES); p.add_argument("--checkpoint"); p.set_defaults(f=cmd_set)
    p = sp.add_parser("commit"); p.add_argument("unit"); p.add_argument("--status", choices=["DONE", "PARTIAL"], default="DONE")
    p.add_argument("--action", default="analyze"); p.add_argument("--note"); p.set_defaults(f=cmd_commit)
    p = sp.add_parser("log"); p.add_argument("--action", required=True); p.add_argument("--units", nargs="*"); p.add_argument("--note"); p.set_defaults(f=cmd_log)
    p = sp.add_parser("index"); p.set_defaults(f=cmd_index)

    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
