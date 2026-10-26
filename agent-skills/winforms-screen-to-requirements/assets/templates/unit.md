---
unit: <UNIT-ID>
module: <MODULE>
type: SCR | CMP | SVC | RPT | JOB | DB | INT
aliases: [<class name>, <caption>]
sources: [<source file paths>]
---
(Status, rev and hashes live in STATE.json; do not repeat them here.)

# <UNIT-ID> - <Business name of the unit>

- **Source**: <file:class> (list every file: .cs, .Designer.cs, .resx, SP, rdlc...)
- **Screenshot**: screenshots/<UNIT-ID>.png (if supplied)
- **Called from**: <unit/menu/button, parameters passed>
- **Calls**: <other units by ID>

## 1. Business purpose
Which user does what with it, in what context.

## 2. Actors and permissions
| Role | Allowed actions | Source |

## 3. Inputs / outputs
Parameters when opened, data returned, DialogResult, global state read/written.

## 4. UI inventory
| Control | Type | Label/caption | Data source | Required | Editable | Default | Format/constraint | Notes |

## 5. Actions and events (Coverage)
| Event/handler | Fires when | Behavior | Related REQ |
(Every handler. No business logic -> say so and why.)

## 6. Requirements
(REQ entries, Origin: LEGACY, in the format of requirement.md.)

## 7. Business rules
| BR-ID | Rule (IF...THEN / Given-When-Then) | Source (file:method:line) | Confidence | Assessment (-> IMP) |

## 8. Characteristic business functions (FN)
One FN entry per auto-calculated/auto-filled field (format of fn.md). "None" if none.

## 9. Data access
| Operation | Table/SP | Read/Write | Filter/sort | Transaction | Source |

## 10. Messages and error handling
| Message text | Condition | Kind (info/warn/error/confirm) | Consequence |

## 11. Business flow
Main, alternative and error flows; state diagram if the data has a lifecycle.

## 12. Legacy quirks
Suspected bugs, odd rules, magic numbers. Each with Decision: Keep / Drop / Ask.

## 13. Assessment and improvements (IMP)
IMPs raised from this unit (format of imp.md) with status.

## 14. Open questions

## 15. New / changed requirements from the user
Full REQ entries for `Origin: NEW` and `CHANGED`. Superseded or dropped legacy REQs stay in section 6 with only their Status changed and a pointer here.
