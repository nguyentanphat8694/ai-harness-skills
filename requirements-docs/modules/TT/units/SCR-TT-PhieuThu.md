---
unit: SCR-TT-PhieuThu
module: TT
type: SCR
aliases: [frmPhieuThu, "PHIẾU THU TIỀN"]
sources: [Hospita.View/Thu Tien/frmPhieuThu.cs, Hospita.View/Thu Tien/frmPhieuThu.Designer.cs, Hospital.Model/Dba/NTPObPhieuThu.cs, Hospital.Model/Keylist/New/KeysListObPhieuThu.cs]
---

# SCR-TT-PhieuThu - Payment receipt (Phiếu thu tiền)

- **Source**: `frmPhieuThu` (.cs, .Designer.cs); persistence in `NTPObPhieuThu`, `KeysListObPhieuThu`, `NTPObCTChiDinh`, `NTPObTKBenhNhan`
- **Called from**: `UDSChoThuTien.viewDanhSach_DoubleClick` -> `SetNew(TT010110)` (new receipt for a waiting patient); `UDSDaThu` double-click -> `SetModify(ObPhieuThu)` (open an issued receipt; refused with "Phiếu đã hủy" if cancelled). Both shown with `ShowDialog()`.
- **Calls**: `RPT-TT-PhieuThu` (`RP020100`, print), `SVC-SHARED-TonKho` (stock lookup), `CMP-TT-DSChoThuTien`, `CMP-TT-DSDaThu`

## 1. Business purpose
A cashier collects payment for the services/medicines ordered for one patient (`tb_CTChiDinh` lines), applies a discount and any advance payments (tạm ứng) the patient already made, records the amount tendered and the change due, saves a receipt number, can print it, and can cancel it (releasing the lines and advances).

## 2. Actors and permissions
| Role | Allowed actions | Source |
|---|---|---|
| Any logged-in user | Open, save, print, cancel. No role check exists in this form. | frmPhieuThu.cs (none found) |
| Cashier ("Người thu") | Chosen from `lkNguoiThu`, defaults to `MainNTP.User.TTChung.MaNS` | frmPhieuThu.cs:InitDisplay:80 |

## 3. Inputs / outputs
- Input: `SetNew(TT010110 cls)` (patient `MaBN` + `listCTChiDinh` lines) or `SetModify(ObPhieuThu)`.
- Output: no DialogResult used; the caller list is not refreshed from a return value.
- Global state read: `MainNTP.User`, `MainNTP._Ngay`, lookup lists (`ObDMNhanSuList`, `ObCustomerList`, `ObDMDichVuList`, `ObDichVuTonList`), `DadaConnect.connect_string`.
- Global state written: `MainNTP.ObPhieuThuList`, `ObCTChiDinhList`, `ObTKBenhNhanList`, `ObRecordList` (change log).

## 4. UI inventory
| Control | Type | Label | Data source | Required | Editable | Default | Format / constraint | Notes |
|---|---|---|---|---|---|---|---|---|
| teSoPhieu | TextEdit | Số phiếu | `ObPhieuThu.Ma` | - | no (assigned on save) | empty | - | |
| deNgay | DateEdit | Ngày thu | `MainNTP._Ngay` | - | yes (not in modify) | server business date | - | not validated |
| lkNguoiThu | LookUpEdit | Người thu | `MainNTP.ObDMNhanSuList` | yes | yes (not in modify) | current user's staff code | - | |
| teMaBN | TextEdit | Mã | `cls.MaBN` | yes | set by code | from caller | - | triggers patient info fill |
| teHoTen, teNam, cheNam, teDiaChi | Text/Check | Họ tên, Năm sinh, Nam, Địa chỉ | `ObCustomer` | - | read-only display | - | `cheNam` checked when `Gioitinh == 0` | |
| gridDanhSach / viewDanhSach | GridControl | DANH SÁCH DỊCH VỤ | `listDichVu` | - | rows can be deleted via context menu | - | columns: Mã dịch vụ, Tên, SL, Đơn giá, Thành tiền, Trạng thái thu | |
| mnXoaDong | context menu | Xóa dòng | - | - | enabled unless read-only | - | - | |
| teTongCP | TextEdit | Tổng chi phí | computed | - | read-only | - | `n0` | |
| teSoGiam | TextEdit | Số giảm | user | no | yes (not in modify) | empty = 0 | parsed by `MainNTP.ParseDouble` | |
| teTamUng | TextEdit | Tạm ứng | computed from `tb_TKBenhNhan` | - | read-only display | - | `n0` | |
| teThanhToan | TextEdit | Thanh toán | computed | - | read-only | - | `n0` | |
| teKHTra | TextEdit | K/H Trả | user | no | yes | empty = 0 | parsed | amount tendered |
| teTienThoi | TextEdit | Tiền thói (typo of "thối") | computed | - | read-only | - | `n0` | |
| btLuu | Button | LƯU PHIẾU THU | - | - | disabled in modify mode | - | - | |
| btIn | Button | IN PHIẾU THU | - | - | disabled after `SetNew`, enabled after save | - | - | |
| btHuy | Button | HỦY PHIẾU THU | - | - | same as btIn | - | - | |
| btExit | Button | THOÁT | - | - | yes | - | - | |
| btSave | Button | LƯU ĐĂNG KÝ F2 | - | - | - | - | - | declared in Designer, no click handler found (see Q-003) |

## 5. Actions and events (Coverage)
| Event/handler | Fires when | Behavior | Related REQ |
|---|---|---|---|
| `frmPhieuThu()` ctor | form created | `LoadData` (set date; load Customer/DMPK/DMDichVu/DMNhanSu/DMDonVi caches), `InitDisplay` (staff list, default cashier) | REQ-TT-PhieuThu-001 |
| `teMaBN_EditValueChanged` | patient code changes | fills name, birth year, gender check, address from `ObCustomerList` | REQ-TT-PhieuThu-002 |
| `teSoGiam_EditValueChanged` | discount edited | recompute payment and change | REQ-TT-PhieuThu-004, FN-TT-002 |
| `teKHTra_EditValueChanged` | tendered edited | recompute payment and change | REQ-TT-PhieuThu-004, FN-TT-003 |
| `teTienThoi_EditValueChanged` | change text changes | calls `TinhThanhTien` again (redundant; terminates because the text stops changing) | REQ-TT-PhieuThu-004 |
| `btLuu_Click` | Save | `Save()` | REQ-TT-PhieuThu-005, -006 |
| `btHuy_Click` | Cancel receipt | `Huy()` | REQ-TT-PhieuThu-007 |
| `btIn_Click` | Print | `InPhieuThu()` | REQ-TT-PhieuThu-008 |
| `mnXoaDong_Click` | context menu | `viewDanhSach.DeleteSelectedRows()`; totals are NOT recomputed | REQ-TT-PhieuThu-009 |
| `btExit_Click` | Exit | closes form, no unsaved-change prompt | REQ-TT-PhieuThu-001 |

## 6. Requirements

### REQ-TT-PhieuThu-001 - Open receipt in new or view mode
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall open the receipt form either for a waiting patient (new receipt, with that patient's pending service lines) or for an issued receipt (read-only), and shall initialise the date to the business date and the cashier to the logged-in user's staff code.
- **Trigger / Preconditions**: double-click a row in the waiting list or the paid list; a cancelled receipt cannot be opened ("Phiếu đã hủy").
- **Main flow**: new: lines, patient, advances loaded, Save enabled, Print/Cancel disabled. Modify: receipt loaded, fields read-only, Save and context menu disabled.
- **Alternative / error flows**: no lines found for a receipt -> form opens with an empty grid.
- **Related business rules**: BR-TT-001
- **Acceptance criteria**: Given a cancelled receipt When the user double-clicks it in the paid list Then the message "Phiếu đã hủy" shows and the form does not open.
- **Legacy source**: UDSDaThu.cs:viewChidinh_DoubleClick:150; frmPhieuThu.cs:SetNew:106, SetModify:132
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: Suspect -> IMP-TT-004
- **Links**: -

### REQ-TT-PhieuThu-002 - Show patient details
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall display the patient's name, birth year, gender and full address when the patient code is set.
- **Trigger / Preconditions**: `teMaBN` changes and is non-empty and found in the customer cache.
- **Main flow**: copy `Ten`, `Namsinh`, `DiaChiFull`; tick "Nam" when `Gioitinh == 0`.
- **Alternative / error flows**: unknown patient -> fields keep previous values (not cleared).
- **Related business rules**: -
- **Acceptance criteria**: Given patient with Gioitinh 0 When shown Then the "Nam" box is ticked.
- **Legacy source**: frmPhieuThu.cs:teMaBN_EditValueChanged:282
- **Confidence**: Inferred (meaning of Gioitinh 0 not confirmed, Q-004)
- **Decision**: Keep
- **Assessment**: OK
- **Links**: -

### REQ-TT-PhieuThu-003 - Load advances (tạm ứng) for the patient
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall sum the patient's advance payments that are not cancelled and not yet settled, and show the total as "Tạm ứng"; for an issued receipt, it shall show the advances settled against that receipt.
- **Trigger / Preconditions**: `SetNew` / `SetModify`.
- **Main flow**: new: `tb_TKBenhNhan` rows for `MaBN` where `TrangThai` not in (Đã_hủy, Đã_hạch_toán), sum of `ThanhTien`. Modify: rows with `TrangThai = Đã_hạch_toán` and `KeyPT = receipt Ma`.
- **Alternative / error flows**: none found -> 0.
- **Related business rules**: BR-TT-002
- **Acceptance criteria**: Given advances 500,000 (Đã_thu) and 200,000 (Đã_hạch_toán) When opening a new receipt Then Tạm ứng = 500,000.
- **Legacy source**: frmPhieuThu.cs:SetNew:122-129, SetModify:146-153
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: OK
- **Links**: FN-TT-002

### REQ-TT-PhieuThu-004 - Calculate totals live
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall compute Tổng chi phí, Thanh toán and Tiền thối and refresh Thanh toán and Tiền thối whenever the discount or the amount tendered changes.
- **Trigger / Preconditions**: lines loaded; discount or tendered edited.
- **Main flow**: see FN-TT-001..003.
- **Alternative / error flows**: before lines are loaded, nothing is computed.
- **Related business rules**: BR-TT-003
- **Acceptance criteria**: Given lines 2x100,000 and 1x50,000, discount 20,000, advance 30,000, tendered 250,000 When computing Then Thanh toán = 200,000 and Tiền thối = 50,000.
- **Legacy source**: frmPhieuThu.cs:TinhThanhTien:98-104
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: Suspect -> IMP-TT-002
- **Links**: FN-TT-001, FN-TT-002, FN-TT-003

### REQ-TT-PhieuThu-005 - Validate before saving
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall refuse to save unless a patient is chosen, a cashier is chosen, at least one line exists, and every non-service line has enough stock.
- **Trigger / Preconditions**: Save clicked.
- **Main flow**: checks in this order, each with its own message (section 10); stop at the first failure.
- **Alternative / error flows**: item missing from the service catalogue is skipped by the stock check.
- **Related business rules**: BR-TT-004
- **Acceptance criteria**: Given a medicine line SL 5 and stock 3 When saving Then "Số lượng tồn không đủ bán(3<5)" shows and nothing is saved.
- **Legacy source**: frmPhieuThu.cs:KiemTraHopLe:156-187
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: Suspect -> IMP-TT-003
- **Links**: -

### REQ-TT-PhieuThu-006 - Save a new receipt
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall, on a valid save, assign the next receipt number, store the receipt with status "Đã_thu", attach every line to the receipt, mark the patient's advances as settled against it, lock the form to read-only and enable Print and Cancel.
- **Trigger / Preconditions**: validation passed.
- **Main flow**: `Ma = Max(Ma)+1`; insert `tb_PhieuThu` (date, cashier, patient, status, discount, serialized payment info incl. tendered and payment); set `KeyPT` on each `tb_CTChiDinh`; set each advance to `Đã_hạch_toán` with `KeyPT`; message "Tạo phiếu thu thành công".
- **Alternative / error flows**: no transaction; a failure midway leaves partial data. Modify-mode save path exists but is unreachable because Save is disabled (Q-002).
- **Related business rules**: BR-TT-005, BR-TT-006
- **Acceptance criteria**: Given a valid new receipt When saved Then a receipt with number Max+1 exists, all its lines have `KeyPT` = that number and the advances are `Đã_hạch_toán`.
- **Legacy source**: frmPhieuThu.cs:Save:199-223, SaveCTChiDinh:189, UpdateTKBenhNhan:225; NTPObPhieuThu.cs:GetNextID:15
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: Suspect -> IMP-TT-001, IMP-TT-005
- **Links**: -

### REQ-TT-PhieuThu-007 - Cancel a receipt
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall, after confirmation, set the receipt status to "Đã_hủy", release all its lines (`KeyPT = 0`), return its advances to "Đã_thu", and close the form.
- **Trigger / Preconditions**: a receipt is loaded; user confirms "Bạn có chắc chắn muốn hủy phiếu này?".
- **Main flow**: status update, release lines, `UpdateTKBenhNhan(true)`, message "Hủy thành công phiếu thu".
- **Alternative / error flows**: user answers No -> nothing changes.
- **Related business rules**: BR-TT-007
- **Acceptance criteria**: Given a saved receipt with 3 lines When cancelled Then its status is Đã_hủy and the 3 lines have `KeyPT = 0`.
- **Legacy source**: frmPhieuThu.cs:Huy:250-266
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: Suspect -> IMP-TT-006
- **Links**: -

### REQ-TT-PhieuThu-008 - Print the receipt
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Must
- **Statement**: The system shall show a print preview of the receipt built from the stored receipt and its lines.
- **Trigger / Preconditions**: receipt exists (`obCur != null`).
- **Main flow**: build `TT020110` from the receipt and `GetListOb_KeyPT`; open `RP020100` with report type `Phieu_Thu`.
- **Alternative / error flows**: no receipt -> nothing happens.
- **Related business rules**: -
- **Acceptance criteria**: Given a saved receipt When Print is clicked Then a preview with its lines is shown.
- **Legacy source**: frmPhieuThu.cs:InPhieuThu:268
- **Confidence**: Certain
- **Decision**: Keep
- **Assessment**: OK
- **Links**: -

### REQ-TT-PhieuThu-009 - Remove a line before saving
- **Origin**: LEGACY
- **Status**: ACTIVE
- **Priority**: Should
- **Statement**: The system shall let the cashier delete the selected line from the grid on a new receipt, so it is not included in the receipt.
- **Trigger / Preconditions**: context menu "Xóa dòng", not read-only.
- **Main flow**: `viewDanhSach.DeleteSelectedRows()`.
- **Alternative / error flows**: totals are not recomputed after deletion (legacy quirk).
- **Related business rules**: -
- **Acceptance criteria**: Given 3 lines When one is deleted Then only the 2 remaining are saved with the receipt.
- **Legacy source**: frmPhieuThu.cs:mnXoaDong_Click:318
- **Confidence**: Inferred (grid is bound to `listDichVu`, so deletion should remove from the list)
- **Decision**: Ask
- **Assessment**: Wrong -> IMP-TT-002
- **Links**: FN-TT-001

## 7. Business rules
| BR-ID | Rule | Source | Confidence | Assessment (-> IMP) |
|---|---|---|---|---|
| BR-TT-001 | IF receipt status = Đã_hủy THEN it cannot be opened from the paid list | UDSDaThu.cs:155 | Certain | OK |
| BR-TT-002 | Advances counted for a new receipt = not Đã_hủy and not Đã_hạch_toán | frmPhieuThu.cs:125 | Certain | OK |
| BR-TT-003 | Totals use line `SL * DG` only; line-level discount (`SoGiam`) and stored `ThanhTien` are ignored | frmPhieuThu.cs:118 | Certain | Suspect -> IMP-TT-002 |
| BR-TT-004 | Stock is checked only for lines whose catalogue item is not of type Dịch_vụ; item missing from catalogue is skipped; stock comes from the in-memory cache | frmPhieuThu.cs:175-184; KeyslistObSLTon.cs:12 | Certain | Suspect -> IMP-TT-003 |
| BR-TT-005 | New receipt status is always "Đã_thu" | frmPhieuThu.cs:38 | Certain | OK |
| BR-TT-006 | Receipt number = Max(Ma)+1 over `tb_PhieuThu` (float column) | NTPObPhieuThu.cs:15 | Certain | Suspect -> IMP-TT-001 |
| BR-TT-007 | Cancelling returns advances to "Đã_thu" and sets `KeyPT = 0` on lines | frmPhieuThu.cs:225-248 | Certain | OK |

## 8. Characteristic business functions (FN)

#### FN-TT-001 - Total cost
- **Trigger**: after lines are loaded (`SetNew`, `SetModify`); NOT after a row is deleted
- **Inputs**: lines: SL (number) | DG (unit price, number)
- **Outputs**: teTongCP | text `n0` | read-only | recomputed each time
- **Algorithm**: `TongCP = Σ(SL × DG)` over all lines; text formatted with `ToString("n0")` using the current culture
- **Edge cases and errors**: no lines -> 0; negative values not guarded; rounding by `n0` display only
- **Dependencies**: -
- **Test vectors**: [2x100000, 1x50000] -> 250,000 (derived from code); [] -> 0 (derived from code); [1x0.5] -> 1 (display rounding of `n0`, derived from code)
- **Source**: frmPhieuThu.cs:118, 143
- **Assessment**: Suspect -> IMP-TT-002

#### FN-TT-002 - Amount to pay
- **Trigger**: any change of discount or tendered; after loading
- **Inputs**: TongCP | SoGiam (user) | TamUng; each parsed with `MainNTP.ParseDouble` (empty or unparsable -> 0, current culture, `NumberStyles.Any`)
- **Outputs**: teThanhToan | stored in `TTChung.ThanhToan` on save
- **Algorithm**: `ThanhToan = TongCP − SoGiam − TamUng`; shown with `n0`
- **Edge cases and errors**: can be negative (advance or discount larger than total); discount above total not blocked
- **Dependencies**: FN-TT-001, REQ-TT-PhieuThu-003
- **Test vectors**: 250,000 − 20,000 − 30,000 -> 200,000 (code); 100,000 − 0 − 150,000 -> −50,000 (edge, code); "abc" as discount -> treated as 0 (code)
- **Source**: frmPhieuThu.cs:100-101
- **Assessment**: Suspect -> IMP-TT-002

#### FN-TT-003 - Change due
- **Trigger**: same as FN-TT-002
- **Inputs**: KHTra (tendered) | ThanhToan
- **Outputs**: teTienThoi | read-only | not stored
- **Algorithm**: `TienThoi = KHTra − ThanhToan`; `n0`
- **Edge cases and errors**: negative when tendered is less than payable; nothing blocks saving
- **Dependencies**: FN-TT-002
- **Test vectors**: 250,000 − 200,000 -> 50,000 (code); 0 − 200,000 -> −200,000 (edge, code); 200,000 − 200,000 -> 0 (code)
- **Source**: frmPhieuThu.cs:102-103
- **Assessment**: OK

## 9. Data access
| Operation | Table/SP | Read/Write | Filter/sort | Transaction | Source |
|---|---|---|---|---|---|
| Next number | tb_PhieuThu | R | `Max(Ma)` | none | NTPObPhieuThu.cs:15 |
| Insert receipt | tb_PhieuThu | W | - | none | NTPObPhieuThu.cs:167 |
| Update status | tb_PhieuThu | W | `Ma` | none | NTPObPhieuThu.cs:299 |
| Lines of a receipt | tb_CTChiDinh | R | `KeyPT = receipt` | none | NTPObCTChiDinh.GetListOb_KeyPT |
| Attach/release lines | tb_CTChiDinh | W | `Ma` (UPDATE incl. `KeyPT`) | none, one update per line | NTPObCTChiDinh.cs:493 |
| Patient advances | tb_TKBenhNhan | R | `MaBN` | none | NTPObTKBenhNhan.cs:153 |
| Settle/restore advances | tb_TKBenhNhan | W | `ID` | none | NTPObTKBenhNhan.cs:64 |
| Stock | in-memory `ObDichVuTonList` (view `vw_SLTon` exists in `NTPObSLTon`, not used here) | R | `Ma = MaDV` | - | KeyslistObSLTon.cs:12 |
| Change log | `ObRecordList` | W | per insert/update | - | KeysListObPhieuThu.cs:28 |

## 10. Messages and error handling
| Message text | Condition | Kind | Consequence |
|---|---|---|---|
| "Vui lòng chọn bệnh nhân" | patient code empty | warn | save aborted |
| "Vui lòng chọn người thu" | cashier empty | warn | save aborted |
| "Không có dịch vụ để thu" | no lines | warn | save aborted |
| "Số lượng tồn không đủ bán(" + stock + "<" + SL + ")" | non-service line SL above stock | error | save aborted |
| "Tạo phiếu thu thành công" | after save | info | form becomes read-only |
| "Bạn có chắc chắn muốn hủy phiếu này?" | Cancel clicked | confirm | No -> nothing |
| "Hủy thành công phiếu thu" | after cancel | info | form closes |
| "Phiếu đã hủy" (in `UDSDaThu`) | opening a cancelled receipt | warn | form not opened |

## 11. Business flow
Main: waiting list -> double-click patient -> lines and advances loaded -> cashier enters discount and tendered -> Save -> Print.
Cancel: paid list -> open receipt -> Cancel -> confirm -> lines released, advances restored.
Receipt data lifecycle: (none) -> `Đã_thu` -> `Đã_hủy`.
Advance lifecycle (`tb_TKBenhNhan`): `Đã_thu` -> `Đã_hạch_toán` (on receipt save) -> `Đã_thu` (on receipt cancel); `Đã_hủy` excluded.
Other concerns: permissions none; audit via `CreateBy/UpdateBy` and `ObRecordList`; concurrency none; transaction none.

## 12. Legacy quirks
- Label typo "Tiền thói" (should be "thối"). Decision: Ask.
- Row deletion does not recompute totals (REQ-009). Decision: Ask.
- `teTienThoi_EditValueChanged` calls `TinhThanhTien` redundantly. Decision: Drop in rewrite (no business meaning).
- Receipt number via `Max+1` on a float column. Decision: Ask.
- Print and Cancel are disabled after `SetNew` and enabled after Save, but `SetModify` never sets them (Q-005). Decision: Ask.
- Unused `btSave` "LƯU ĐĂNG KÝ F2" copied from another form (Q-003). Decision: Drop.

## 13. Assessment and improvements (IMP)

### IMP-TT-001 - Receipt number can collide under concurrent cashiers
- **Applies to**: REQ-TT-PhieuThu-006, BR-TT-006
- **Type / Severity**: Concurrency / High
- **Current behavior (evidence)**: `Max(Ma)+1` read, then inserted later without lock or unique retry (NTPObPhieuThu.cs:15, frmPhieuThu.cs:206).
- **Why it is questionable / impact**: two cashiers saving at the same time can get the same number.
- **Suggestion**: database-generated sequence/identity, or insert with retry on key violation.
- **Alternatives / trade-offs**: keep gapless numbering with a locked counter table.
- **Needs confirmation from**: user (is gapless numbering required by accounting?)
- **Status**: PROPOSED

### IMP-TT-002 - Totals ignore line discounts and go stale after deleting a row
- **Applies to**: REQ-TT-PhieuThu-004, REQ-009, BR-TT-003, FN-TT-001, FN-TT-002
- **Type / Severity**: Logic error / High
- **Current behavior (evidence)**: Total = Σ SL×DG, never recomputed after `DeleteSelectedRows` (frmPhieuThu.cs:118, 320); `ObCTChiDinh` also carries `SoGiam` and `ThanhTien` columns that are not used.
- **Why it is questionable / impact**: deleting a line leaves the payable amount too high; line-level discounts, if used elsewhere, are not reflected.
- **Suggestion**: recompute totals after any row change; confirm whether line discounts exist in practice.
- **Alternatives / trade-offs**: disallow row deletion on this screen.
- **Needs confirmation from**: user
- **Status**: PROPOSED

### IMP-TT-003 - Stock check uses an in-memory cache and runs only at save
- **Applies to**: REQ-TT-PhieuThu-005, BR-TT-004
- **Type / Severity**: Data-integrity risk / Medium
- **Current behavior (evidence)**: `KeysListObSLTon.GetSLTon` reads `MainNTP.ObDichVuTonList` (KeyslistObSLTon.cs:12); a DB-based `NTPObSLTon.GetSLTon` over `vw_SLTon` exists but is not used.
- **Why it is questionable / impact**: stale cache on a multi-user system allows overselling.
- **Suggestion**: check stock against the database inside the save transaction.
- **Alternatives / trade-offs**: refresh cache before checking.
- **Needs confirmation from**: user
- **Status**: PROPOSED

### IMP-TT-004 - No role check for collecting or cancelling payments
- **Applies to**: REQ-TT-PhieuThu-001, REQ-007
- **Type / Severity**: Security/permissions / Medium
- **Current behavior (evidence)**: no permission call found in frmPhieuThu.cs.
- **Why it is questionable / impact**: any user can cancel receipts.
- **Suggestion**: restrict cancel to authorised roles and log reason.
- **Alternatives / trade-offs**: require supervisor confirmation.
- **Needs confirmation from**: user
- **Status**: PROPOSED

### IMP-TT-005 - Save is not atomic
- **Applies to**: REQ-TT-PhieuThu-006
- **Type / Severity**: Data-integrity risk / High
- **Current behavior (evidence)**: receipt insert, per-line updates and advance updates run as separate commands (frmPhieuThu.cs:206-217).
- **Why it is questionable / impact**: a failure midway leaves a receipt without its lines or advances still unsettled.
- **Suggestion**: wrap in one transaction.
- **Alternatives / trade-offs**: compensating rollback.
- **Needs confirmation from**: user
- **Status**: PROPOSED

### IMP-TT-006 - No validation of amounts (negative payable, short tender, discount above total)
- **Applies to**: REQ-TT-PhieuThu-004, REQ-006, FN-TT-002, FN-TT-003
- **Type / Severity**: Missing validation/edge case / Medium
- **Current behavior (evidence)**: payable and change may be negative and the receipt still saves (frmPhieuThu.cs:100-103, 199).
- **Why it is questionable / impact**: receipts with impossible amounts can be issued.
- **Suggestion**: block or warn on discount > total and on tendered < payable; define handling of advance exceeding total (refund).
- **Alternatives / trade-offs**: allow partial payment as a distinct feature.
- **Needs confirmation from**: user (business policy on partial payment and refund of advance)
- **Status**: PROPOSED

## 14. Open questions
Q-001 .. Q-005 are listed in OPEN-QUESTIONS.md (enum definitions, unreachable modify-save, unused `btSave`, gender code meaning, button state in modify mode).

## 15. New / changed requirements from the user
None.
