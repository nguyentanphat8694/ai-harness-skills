---
unit: SCR-REC-Receipt
module: REC
type: SCR
aliases: [frmReceipt, "PHIẾU THU TIỀN"]
sources: [Forms/frmReceipt.cs, Forms/frmReceipt.Designer.cs]
---

# SCR-REC-Receipt - Payment receipt (PHIẾU THU TIỀN)

- **Source**: `Forms/frmReceipt.cs` (class `frmReceipt : DevExpress.XtraEditors.XtraForm`), `Forms/frmReceipt.Designer.cs`; DAL `Model/ReceiptDal.cs`; enums `Model/Enums.cs` (UTF-16 file).
- **Screenshot**: none supplied; screen identified from text (title and 6 labels + 2 buttons, 9/9 match by `find_screen.py`).
- **Called from**: main ribbon button `btnReceipt` "PHIẾU THU" -> `frmMain.OpenReceipt()` (App/frmMain.cs:7-16). Modeless, single instance (re-click activates the open window). No parameters.
- **Calls**: `SCR-REC-ReceiptPrint` (btnPrint, modal, no parameters). Unresolved external code: `StockDal.GetStock`, `Db`, `Receipt`, `ReceiptLine` (see Q-001).

## 1. Business purpose
A cashier collects payment for a patient's drugs and services: shows total, applies a discount, shows the amount payable, takes the cash the customer hands over and shows change, then saves the receipt (status Paid) and can print it.

## 2. Actors and permissions
| Role | Allowed actions | Source |
|---|---|---|
| Any logged-in user | Open and use the screen; no role check found in this form or in frmMain handlers | frmMain.cs:17; frmReceipt.cs (none) |

Session.CurrentUser is set at login (App/frmLogin.cs:14) but is not used on this screen: the receipt does not record who created it (see IMP-REC-004).

## 3. Inputs / outputs
Inputs: none from the opener. Output: new row in `tb_Receipt`, lines linked in `tb_Line`. Global state: none read; opens `frmReceiptPrint` without passing the receipt.

## 4. UI inventory
| Control | Type | Label/caption | Data source | Required | Editable | Default | Format/constraint | Notes |
|---|---|---|---|---|---|---|---|---|
| `frmReceipt` | Form | "PHIẾU THU TIỀN" (Receipt) | - | - | - | - | - | Designer:5 |
| `txtPatient` | text edit | lblPatient "Mã bệnh nhân" (Patient code) | typed by user (no lookup code found) | Yes (Validate) | Yes | empty | free text | not in Designer excerpt; used at cs:28,44 |
| `lines` | `List<ReceiptLine>` (grid not in source) | - | unknown | >=1 line | unknown | empty | Qty, Price, Code, Type | no code adds rows (Q-002) |
| `mnuDeleteRow` | context menu item | "Xóa dòng" (Delete row) | - | - | - | - | - | Designer:18; no handler (Q-002) |
| `txtTotal` | text edit | lblTotal "Tổng tiền" (Total) | computed | - | No (ReadOnly) | - | `n0` | Designer:12 |
| `txtDiscount` | text edit | lblDiscount "Giảm giá" (Discount) | user | No | Yes | empty (=0) | parsed as double, `n0` not applied to input | EditValueChanged -> Recalc |
| `txtPayable` | text edit | lblPayable "Phải thu" (Amount due) | computed | - | No (ReadOnly) | - | `n0` | Designer:13 |
| `txtTendered` | text edit | lblTendered "Khách đưa" (Cash given) | user | No | Yes | empty (=0) | parsed as double | EditValueChanged -> Recalc |
| `txtChange` | text edit | lblChange "Tiền thối" (Change) | computed | - | No (ReadOnly) | - | `n0` | Designer:14 |
| `btnSave` | button | "LƯU" (Save) | - | - | enabled always | - | - | |
| `btnPrint` | button | "IN PHIẾU" (Print receipt) | - | - | disabled until first successful save | Enabled=false | - | Designer:17; enabled at cs:49 |

## 5. Actions and events (Coverage)
| Event/handler | Fires when | Behavior | Related REQ |
|---|---|---|---|
| `btnSave_Click` (cs:41) | click LƯU | validate, create receipt, link lines, confirm, enable print | REQ-REC-Receipt-003, -004, -005 |
| `btnPrint_Click` (cs:52) | click IN PHIẾU | open `frmReceiptPrint` modally | REQ-REC-Receipt-006 |
| `txtDiscount_EditValueChanged` (cs:57) | discount text changes | `Recalc()` | REQ-REC-Receipt-002 |
| `txtTendered_EditValueChanged` (cs:58) | cash given changes | `Recalc()` | REQ-REC-Receipt-002 |
| `Recalc` / `Parse` / `Validate` (helpers) | called by handlers | totals, number parsing, validation | REQ-REC-Receipt-002, -003 |
| `mnuDeleteRow` | (no handler wired) | none found: no business logic in source | REQ-REC-Receipt-007 (Ask) |
| `OpenReceipt` in frmMain (frmMain.cs:7) | menu click | single-instance open | REQ-REC-Receipt-001 |

## 6. Requirements

### REQ-REC-Receipt-001 - Open receipt screen as single instance
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall open the receipt screen from the main menu as a non-modal window and, if it is already open, bring the existing one to front instead of opening a second.
- **Trigger / Preconditions**: user clicks "PHIẾU THU" in main menu.
- **Main flow**: no instance -> create and show; instance closed -> reference cleared.
- **Alternative / error flows**: instance open -> `Activate()`.
- **Related business rules**: BR-REC-001
- **Acceptance criteria**: Given receipt window open, When user clicks the menu again, Then no new window appears and the existing one is focused.
- **Legacy source**: App/frmMain.cs:OpenReceipt:7-16
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: OK

### REQ-REC-Receipt-002 - Show total, amount due and change
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall display read-only Total, Amount due and Change, recalculated when Discount or Cash-given changes (formulas in FN-REC-001..003).
- **Trigger / Preconditions**: edit of `txtDiscount` or `txtTendered`.
- **Main flow**: parse inputs (invalid or empty = 0) -> compute -> display with thousands format `n0`.
- **Alternative / error flows**: non-numeric text counts as 0, no message.
- **Related business rules**: BR-REC-002, BR-REC-003, BR-REC-004
- **Acceptance criteria**: Given total 100,000 and discount 10,000, When cash given is 100,000, Then due = 90,000 and change = 10,000.
- **Legacy source**: Forms/frmReceipt.cs:Recalc:11-18; :57-58
- **Confidence**: Certain (recalc on line change: Inferred, Q-002)
- **Decision**: Keep
- **Assessment**: Suspect -> IMP-REC-002, IMP-REC-003
- **Links**: FN-REC-001, FN-REC-002, FN-REC-003

### REQ-REC-Receipt-003 - Validate before saving
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall refuse to save, with a message, when no patient code is entered, when there are no lines, or when any Drug line quantity exceeds current stock; checks run in that order and stop at the first failure.
- **Trigger / Preconditions**: click LƯU.
- **Main flow**: patient empty -> "Vui lòng chọn bệnh nhân"; lines empty -> "Không có dịch vụ để thu"; Drug line with `StockDal.GetStock(Code) < Qty` -> "Không đủ tồn kho: <Code>".
- **Alternative / error flows**: Service lines are not stock-checked.
- **Related business rules**: BR-REC-005, BR-REC-006
- **Acceptance criteria**: Given a Drug line Qty 5 and stock 3, When Save, Then message "Không đủ tồn kho: <Code>" and nothing is saved.
- **Legacy source**: Forms/frmReceipt.cs:Validate:26-39
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: Suspect -> IMP-REC-003 (no check of cash given vs due, discount range)

### REQ-REC-Receipt-004 - Save receipt as Paid
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall, on a valid save, allocate the next receipt Id, insert the receipt with PatientCode, Discount and Status = Paid, link every line to it, show "Đã lưu phiếu thu" and enable the print button.
- **Trigger / Preconditions**: Validate() true.
- **Main flow**: `NextId` = Max(Id)+1 (1 if table empty) -> `Insert` -> `AttachLine` per line -> message -> `btnPrint.Enabled = true`.
- **Alternative / error flows**: no try/catch, no transaction; failure part-way leaves a partial receipt (see IMP-REC-001).
- **Related business rules**: BR-REC-007, BR-REC-008
- **Acceptance criteria**: Given empty tb_Receipt, When a valid receipt is saved, Then Id = 1 and Status = 'Paid'.
- **Legacy source**: Forms/frmReceipt.cs:btnSave_Click:41-50; Model/ReceiptDal.cs:6-20
- **Confidence**: Certain for flow; Ask for what columns really persist (Q-003)
- **Decision**: Keep
- **Assessment**: Wrong -> IMP-REC-001, IMP-REC-004, IMP-REC-005

### REQ-REC-Receipt-005 - Stock is not decremented on save
- **Origin**: LEGACY
- **Status**: NEEDS-REVIEW
- **Priority**: Should
- **Statement**: Legacy only checks stock on save and does not decrease stock in this screen; where (if anywhere) stock is deducted is unknown.
- **Trigger / Preconditions**: save.
- **Main flow**: none found.
- **Alternative / error flows**: -
- **Related business rules**: BR-REC-005
- **Acceptance criteria**: To be defined after Q-004 is answered.
- **Legacy source**: Forms/frmReceipt.cs:btnSave_Click:41-50 (absence of a call); StockDal not in source
- **Confidence**: Ask
- **Decision**: Ask
- **Assessment**: Missing -> IMP-REC-005

### REQ-REC-Receipt-006 - Print receipt
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall allow printing only after a receipt has been saved in this window, by opening the print form modally.
- **Trigger / Preconditions**: `btnPrint.Enabled` (false at start, true after first save).
- **Main flow**: `new frmReceiptPrint().ShowDialog()`. No receipt Id or data is passed; `frmReceiptPrint` has an empty body (see SCR-REC-ReceiptPrint, PENDING).
- **Alternative / error flows**: after a second edit/save the button stays enabled.
- **Related business rules**: BR-REC-009
- **Acceptance criteria**: Given a fresh window, Then IN PHIẾU is disabled; after a successful save it is enabled.
- **Legacy source**: Forms/frmReceipt.cs:btnPrint_Click:52-55; Designer:17
- **Confidence**: Certain for flow; Ask for what the print shows (Q-005)
- **Decision**: Ask
- **Assessment**: Suspect -> IMP-REC-006

### REQ-REC-Receipt-007 - Delete a line (context menu "Xóa dòng")
- **Origin**: LEGACY
- **Status**: NEEDS-REVIEW
- **Priority**: Could
- **Statement**: A context menu item "Xóa dòng" exists on the screen, but no handler is wired in the source; its behavior is unknown.
- **Trigger / Preconditions**: unknown.
- **Main flow**: none found.
- **Alternative / error flows**: -
- **Related business rules**: -
- **Acceptance criteria**: To be defined after Q-002.
- **Legacy source**: Forms/frmReceipt.Designer.cs:InitializeComponent:18
- **Confidence**: Ask
- **Decision**: Ask
- **Assessment**: Missing -> IMP-REC-002

### REQ-REC-Receipt-008 - Source of receipt lines
- **Origin**: LEGACY
- **Status**: NEEDS-REVIEW
- **Priority**: Must
- **Statement**: The receipt lines (`lines`: Code, Type, Qty, Price) must come from somewhere, but no code in the available source populates them (no add, load or grid). Needed to rebuild the screen.
- **Trigger / Preconditions**: unknown.
- **Main flow**: unknown.
- **Alternative / error flows**: -
- **Related business rules**: -
- **Acceptance criteria**: To be defined after Q-002.
- **Legacy source**: Forms/frmReceipt.cs:9 (field declaration only)
- **Confidence**: Ask
- **Decision**: Ask
- **Assessment**: Missing -> IMP-REC-002

## 7. Business rules
| BR-ID | Rule | Source | Confidence | Assessment (-> IMP) |
|---|---|---|---|---|
| BR-REC-001 | Only one receipt window may be open at a time | frmMain.cs:OpenReceipt:9-15 | Certain | OK |
| BR-REC-002 | Total = sum(Qty x Price) of lines | frmReceipt.cs:Recalc:13 | Certain | Suspect -> IMP-REC-002 |
| BR-REC-003 | Amount due = Total - Discount; no limit on Discount (can exceed total, can be negative) | frmReceipt.cs:Recalc:15 | Certain | Suspect -> IMP-REC-003 |
| BR-REC-004 | Change = Cash given - Amount due; may be negative (shown as negative number) | frmReceipt.cs:Recalc:17 | Certain | Suspect -> IMP-REC-003 |
| BR-REC-005 | Drug lines need stock >= Qty at save time; Service lines exempt | frmReceipt.cs:Validate:30-37 | Certain | Suspect -> IMP-REC-005 |
| BR-REC-006 | Patient code and at least one line are mandatory | frmReceipt.cs:Validate:28-29 | Certain | OK |
| BR-REC-007 | Saved receipt always has Status = Paid (eStatus.Paid) | frmReceipt.cs:btnSave_Click:44 | Certain | OK |
| BR-REC-008 | Receipt Id = Max(Id)+1, or 1 when none | ReceiptDal.cs:NextId:8-9 | Certain | Wrong -> IMP-REC-001 |
| BR-REC-009 | Print enabled only after a save in this window | Designer:17; frmReceipt.cs:49 | Certain | Suspect -> IMP-REC-006 |

## 8. Characteristic business functions (FN)

#### FN-REC-001 - Receipt total
- **Trigger**: automatic, inside `Recalc()` on every Discount or Cash-given edit. Does NOT run when `lines` change (no call exists).
- **Inputs**: lines[].Qty, lines[].Price (double) | not rounded | required | no range check
- **Outputs**: `txtTotal` (read-only), text `n0`, recomputed each time, not stored
- **Algorithm**: total = sum over lines of Qty * Price; text = total.ToString("n0") (current culture, rounds to integer for display only).
- **Edge cases and errors**: no lines -> 0; negative qty/price not rejected; double floating-point arithmetic.
- **Dependencies**: `lines`
- **Test vectors**: (1) lines {2 x 50,000; 1 x 30,000} -> 130,000 (derived from code). (2) no lines -> 0. (3) {Qty 1, Price 0.5} x 3 -> 1.5 displays "2" (display rounding, derived from code, culture-dependent).
- **Source**: Forms/frmReceipt.cs:Recalc:13-14
- **Assessment**: Suspect -> IMP-REC-002

#### FN-REC-002 - Amount due
- **Trigger**: `Recalc()`.
- **Inputs**: total (FN-REC-001), Discount text (parsed by `Parse`: invalid/empty -> 0)
- **Outputs**: `txtPayable` read-only, `n0`, recomputed, not stored
- **Algorithm**: payable = total - Parse(txtDiscount.Text).
- **Edge cases and errors**: discount > total -> negative payable; negative discount increases payable; "abc" -> 0; thousand separators typed ("10,000") may parse per culture, otherwise 0.
- **Dependencies**: FN-REC-001
- **Test vectors**: (1) total 130,000, discount 30,000 -> 100,000. (2) discount empty -> 130,000. (3) total 100,000, discount 150,000 -> -50,000 (edge, derived from code).
- **Source**: Forms/frmReceipt.cs:Recalc:15-16, Parse:20-24
- **Assessment**: Suspect -> IMP-REC-003

#### FN-REC-003 - Change to give back
- **Trigger**: `Recalc()`.
- **Inputs**: Cash-given text (parse; invalid/empty -> 0), payable (FN-REC-002)
- **Outputs**: `txtChange` read-only, `n0`, recomputed, not stored
- **Algorithm**: change = Parse(txtTendered.Text) - payable.
- **Edge cases and errors**: cash given empty with payable 100,000 -> -100,000; cash < payable -> negative (no warning); not blocked on save.
- **Dependencies**: FN-REC-002
- **Test vectors**: (1) payable 100,000, given 150,000 -> 50,000. (2) given 100,000 -> 0. (3) given empty, payable 100,000 -> -100,000 (edge).
- **Source**: Forms/frmReceipt.cs:Recalc:17
- **Assessment**: Suspect -> IMP-REC-003

## 9. Data access
| Operation | Table/SP | Read/Write | Filter/sort | Transaction | Source |
|---|---|---|---|---|---|
| Next Id | `tb_Receipt` (`Select Max(Id) From tb_Receipt`) | R | none | none | ReceiptDal.cs:NextId:8 |
| Insert receipt | `tb_Receipt` (Id, PatientCode, Discount, Status) | W | - | none; SqlCommand has no parameters added in the code seen (Q-003) | ReceiptDal.cs:Insert:13 |
| Link lines | `tb_Line` `UPDATE SET ReceiptId=@R WHERE Code=@C` | W | by line Code only | none | ReceiptDal.cs:AttachLine:18 |
| Stock check | `StockDal.GetStock(code)` | R | per Drug line | - | frmReceipt.cs:32 (source not found, Q-001) |

Not used here (but in same DAL): `SumBetween` (sums Discount of Paid receipts - tax report, belongs to frmTaxReport), `RebuildIndex` (`EXEC sp_RebuildIndexes`).

## 10. Messages and error handling
| Message text | Condition | Kind | Consequence |
|---|---|---|---|
| "Vui lòng chọn bệnh nhân" (Please select a patient) | `txtPatient` empty | warn | save aborted |
| "Không có dịch vụ để thu" (No services to charge) | `lines.Count == 0` | warn | save aborted |
| "Không đủ tồn kho: " + Code (Insufficient stock) | Drug line, stock < Qty | error | save aborted |
| "Đã lưu phiếu thu" (Receipt saved) | save completed | info | print enabled |

No exception handling: DB errors are unhandled (crash/default .NET dialog).

## 11. Business flow
Main: open screen -> enter patient code -> lines present -> (optional) discount, cash given -> totals update -> LƯU -> validate -> insert receipt (Paid) -> link lines -> "saved" -> IN PHIẾU enabled -> print form.
Error: any validation failure -> message, stay on screen.
State: receipt is created directly as `Paid`; `Draft` and `Cancelled` exist in `eStatus` but are never set here.

## 12. Legacy quirks
| Quirk | Decision |
|---|---|
| Recalc not triggered when lines change; stale total possible | Ask |
| Negative payable/change allowed; no cash >= due check | Ask |
| `Validate()` hides `Form.Validate` (naming) | Drop (technical) |
| Money stored/handled as `double` | Ask |
| Save button stays enabled after save: pressing twice creates a duplicate receipt | Ask |
| Change/Total/Cash given not persisted | Ask |
| Print form gets no receipt Id | Ask |

## 13. Assessment and improvements (IMP)
### IMP-REC-001 - Save is not atomic and Id is racy
- **Applies to**: REQ-REC-Receipt-004, BR-REC-008
- **Type / Severity**: Data integrity / High
- **Current behavior (evidence)**: Max(Id)+1 then Insert then one UPDATE per line, no transaction (frmReceipt.cs:45-47; ReceiptDal.cs:8). Two cashiers can obtain the same Id; an error after Insert leaves a receipt without lines.
- **Why it is questionable / impact**: duplicate keys, orphan receipts, financial records wrong.
- **Suggestion**: one transaction, DB-generated identity/sequence; rollback on failure.
- **Alternatives / trade-offs**: keep human-readable receipt number separately.
- **Needs confirmation from**: user, accountant
- **Status**: PROPOSED

### IMP-REC-002 - Lines never recalculated, source of lines unknown
- **Applies to**: REQ-REC-Receipt-002, -007, -008, FN-REC-001
- **Type / Severity**: Missing behavior / Medium
- **Current behavior (evidence)**: `Recalc()` is only called from discount and cash handlers (cs:57-58); no code adds/removes lines; "Xóa dòng" has no handler.
- **Why it is questionable / impact**: total could be stale; the rebuild team lacks the line-entry requirement.
- **Suggestion**: recalculate on any line change; define add/remove line explicitly after Q-002.
- **Alternatives / trade-offs**: -
- **Needs confirmation from**: user
- **Status**: PROPOSED

### IMP-REC-003 - No numeric validation of discount and cash
- **Applies to**: REQ-REC-Receipt-002, -003, BR-REC-003, BR-REC-004, FN-REC-002, FN-REC-003
- **Type / Severity**: Validation / Medium
- **Current behavior (evidence)**: Parse returns 0 on bad input (cs:20-24); discount can exceed total (100,000 total, 150,000 discount -> -50,000 due); cash less than due gives negative change; save still allowed.
- **Why it is questionable / impact**: wrong receipts; typos silently become 0.
- **Suggestion**: 0 <= discount <= total; require cash >= due (or allow partial payment explicitly); show an error for non-numeric input.
- **Alternatives / trade-offs**: partial payments may be a real business case.
- **Needs confirmation from**: user, accountant (financial)
- **Status**: PROPOSED

### IMP-REC-004 - Receipt does not store cashier, date, total or cash given
- **Applies to**: REQ-REC-Receipt-004
- **Type / Severity**: Audit / Medium
- **Current behavior (evidence)**: Insert writes only Id, PatientCode, Discount, Status (ReceiptDal.cs:13); Session.CurrentUser unused.
- **Why it is questionable / impact**: no audit trail; total must be rebuilt from lines (and lines are linked only by Code, see IMP-REC-005).
- **Suggestion**: store creator, timestamp, total, payable, cash given, change.
- **Alternatives / trade-offs**: -
- **Needs confirmation from**: user
- **Status**: PROPOSED

### IMP-REC-005 - Stock check without deduction; lines linked by Code only
- **Applies to**: REQ-REC-Receipt-004, -005, BR-REC-005
- **Type / Severity**: Data integrity / High
- **Current behavior (evidence)**: AttachLine updates `tb_Line` `WHERE Code=@C` (ReceiptDal.cs:18), so every row with that Code is re-linked, including other receipts' lines; no stock decrement in this screen; check and write are not atomic.
- **Why it is questionable / impact**: corrupted receipt history; overselling.
- **Suggestion**: link by line Id; deduct stock in the same transaction, with re-check.
- **Alternatives / trade-offs**: stock may be deducted elsewhere (Q-004).
- **Needs confirmation from**: user
- **Status**: PROPOSED

### IMP-REC-006 - Print form is not tied to the receipt; double-save possible
- **Applies to**: REQ-REC-Receipt-006, BR-REC-009
- **Type / Severity**: Usability / Medium
- **Current behavior (evidence)**: `new frmReceiptPrint().ShowDialog()` with no argument (cs:54); LƯU stays enabled after save (cs:49 only enables print).
- **Why it is questionable / impact**: print cannot know which receipt; repeat click on LƯU duplicates the receipt.
- **Suggestion**: pass receipt Id; lock the form (or reset) after save.
- **Alternatives / trade-offs**: -
- **Needs confirmation from**: user
- **Status**: PROPOSED

## 14. Open questions
| Q-ID | Question |
|---|---|
| Q-001 | `StockDal`, `Db`, `Receipt`, `ReceiptLine`, `Session`, `UserDal` are not in the source and `Missing.Core.dll` (csproj HintPath `..\libs\Missing.Core.dll`) is missing. Please supply the DLL/source. |
| Q-002 | How are receipt lines added, edited and deleted (grid, "Xóa dòng")? Where is the patient picked? |
| Q-003 | `Insert` builds a SqlCommand without visible parameter binding: does `Db.Exec` bind them? Which columns does `tb_Receipt` really have? Need DB script. |
| Q-004 | Is stock deducted elsewhere (trigger, SP) after saving a receipt? |
| Q-005 | What must the printed receipt contain (`frmReceiptPrint` is empty in the source)? |

## 15. New / changed requirements from the user
None.
