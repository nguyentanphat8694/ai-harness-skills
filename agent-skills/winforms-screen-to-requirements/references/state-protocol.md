# State protocol (prevents duplication and conflicts across sessions)

`STATE.json` is the single source of truth for status, rev, hashes and ID counters. Unit-file frontmatter holds identity only (unit, module, type, aliases, sources). `INDEX.md` is a generated view; if it disagrees, regenerate it, never hand-edit.

Drive STATE through `scripts/state.py` rather than editing JSON by hand (atomic writes, consistent hashing). Hashes are SHA-1 over LF-normalised bytes so CRLF/LF does not cause false drift on Windows.

## Shape (schema 2)
```json
{
  "schema": 2, "root": "requirements-docs", "source_root": "../legacy/src",
  "hash_method": "sha1-lf", "doc_language": "en",
  "counters": {"REQ-SAN-Exam": 14, "BR-SAN": 9, "FN-SAN": 3, "IMP-SAN": 2, "Q": 11},
  "inventory": {"SCR:frmExam": {"type": "SCR", "class": "frmExam", "files": ["Forms/frmExam.cs"], "caption": "Exam", "unit": "SCR-SAN-Exam"}},
  "menus": [{"caption": "Exam", "opens": ["frmExam"]}],
  "units": {"SCR-SAN-Exam": {"status": "DONE|PARTIAL|IN_PROGRESS|PENDING|STALE", "doc": "modules/SAN/units/SCR-SAN-Exam.md",
     "rev": 3, "doc_hash": "...", "aliases": ["frmExam"], "sources": {"Forms/frmExam.cs": "<hash>"},
     "analyzed_at": "YYYY-MM-DD", "checkpoint": "Designer done + 12/20 handlers", "deps": ["SVC-SAN-DueDate"]}},
  "queue": [], "log": [{"date": "YYYY-MM-DD", "action": "analyze", "units": ["SCR-SAN-Exam"], "note": "+14 REQ"}]
}
```

## Rules
- **A. Session start**: `state.py check`. No STATE yet -> `state.py init` (adopts counters from any existing docs, never overwrites content). Then handle: (1) doc hash mismatch = edited outside the skill: re-read and merge before writing; (2) source drift: unit `STALE`, re-read only the changed parts, log "source drift", list dependents (units whose `deps` include it) for the user - do not mass-mark; (3) `IN_PROGRESS` units: say so briefly and resume from `checkpoint` before new work.
- **B. No duplicate units**: before creating a unit, look up class name, file path and caption in `aliases`/`sources` (`state.py register` enforces this). Never two units for one form.
- **C. No duplicate requirements**: before adding a REQ/BR/FN, search the unit (and `_SHARED`) for the same `file:method` source or same statement; update rather than add.
- **D. Allocate IDs** with `state.py next-id` before writing content. IDs are never reused.
- **E. Commit order**: (1) `state.py set <UNIT> IN_PROGRESS --checkpoint ...`; (2) write the unit file in parts, updating the checkpoint after each; (3) `FUNCTIONS.md`, `IMPROVEMENTS.md`, `MODULE.md`, app-level docs, `OPEN-QUESTIONS.md`; (4) `CHANGELOG.md`; (5) `state.py commit` (hashes, rev, status, log) and `state.py index`. If interrupted, the unit stays `IN_PROGRESS` so the next session knows to review.
- **F. Safe writes**: re-read a file right before editing; replace sections, do not overwrite whole files. A hash mismatch means someone edited it: merge. Text between `<!-- manual:start -->` and `<!-- manual:end -->` belongs to the user; never touch it.
- **G. Contradictions**: if re-reading shows behavior differing from a recorded REQ (same source, unchanged), do not silently fix. Set the REQ `Status: NEEDS-REVIEW`, add a CHANGELOG "DISCREPANCY" entry (old, new, evidence) and tell the user. If the source changed, update and log "SOURCE-DRIFT".
- **H. One truth, one place**: shared rules/FN live in `_SHARED` or the owner unit; elsewhere link by ID. NEW/CHANGED REQs sit in the affected unit.
- **I. End of session**: `state.py log` what was done (action, units, counts of REQ/BR/FN/IMP added or changed).
