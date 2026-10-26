# IMPROVEMENTS (High -> Low)

| IMP-ID | Title | Applies to | Type | Severity | Status | Resulting REQ |
|---|---|---|---|---|---|---|
| IMP-TT-001 | Receipt number can collide under concurrent cashiers | REQ-006, BR-006 | Concurrency | High | PROPOSED | |
| IMP-TT-002 | Totals ignore line discounts and go stale after row delete | REQ-004, REQ-009, FN-001/002 | Logic error | High | PROPOSED | |
| IMP-TT-005 | Save is not atomic | REQ-006 | Data-integrity risk | High | PROPOSED | |
| IMP-TT-003 | Stock check uses in-memory cache | REQ-005 | Data-integrity risk | Medium | PROPOSED | |
| IMP-TT-004 | No role check for collect/cancel | REQ-001, REQ-007 | Security/permissions | Medium | PROPOSED | |
| IMP-TT-006 | No validation of amounts | REQ-004, REQ-006 | Missing validation | Medium | PROPOSED | |
