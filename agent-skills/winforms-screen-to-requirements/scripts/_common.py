"""Shared helpers for the winforms-screen-to-requirements scripts (stdlib only)."""
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

SOURCE_EXTS = {".cs", ".vb", ".resx", ".xaml", ".config", ".settings", ".sql", ".rdlc", ".rpt", ".xsd", ".ini"}
SKIP_DIRS = {"bin", "obj", ".git", ".vs", "packages", "node_modules", "TestResults"}


def read_text(path):
    """Read a text file tolerating BOMs, UTF-16 and legacy code pages."""
    raw = Path(path).read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", errors="replace")
    for enc in ("utf-8-sig", "cp1258", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def file_hash(path):
    """SHA-1 of the file with line endings normalised, so CRLF/LF does not change it."""
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(data).hexdigest()


def fold(s):
    """Lower-case and strip diacritics (so 'Khám thai' matches 'kham thai')."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def walk_source(root, exts=None):
    exts = exts or SOURCE_EXTS
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if Path(f).suffix.lower() in exts:
                yield Path(dirpath) / f


def state_path(root):
    return Path(root) / "STATE.json"


def load_state(root):
    p = state_path(root)
    if not p.exists():
        sys.exit(f"STATE.json not found in {root}. Run: state.py init --root {root} --source <src>")
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(root, state):
    # Write to a temp file then rename so an interrupted run cannot corrupt STATE.json.
    p = state_path(root)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(p)


def today():
    return date.today().isoformat()


ID_RE = re.compile(r"\b(REQ-[A-Z]+-[A-Za-z0-9]+-\d{3}|BR-[A-Z]+-\d{3}|FN-[A-Z]+-\d{3}|IMP-[A-Z]+-\d{3}|Q-\d{3})\b")
