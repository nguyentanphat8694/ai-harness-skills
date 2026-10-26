# Screen: PHIẾU THU TIỀN (Receipt) - frmReceipt

Sources read: Forms/frmReceipt.cs, Forms/frmReceipt.Designer.cs, Forms/frmReceiptPrint.cs, Model/ReceiptDal.cs, Model/Enums.cs, App/frmMain.cs and App/frmMain.Designer.cs (entry point only).
Not read, not in the source set: Db, StockDal, Receipt and ReceiptLine classes. Their behaviour is unknown.

## 1. Purpose
Cashier screen that records a payment for a patient. It shows the amount due, the discount, the cash tendered and the change, saves the receipt, then allows printing.

## 2. Entry and lifecycle
- Opened from the main window's "PHIẾU THU" ribbon/bar button (frmMain.btnReceipt).
- It is a modeless, single-instance form. If it is already open it is activated rather than opened again. The reference is cleared when the form closes.
- Form class: DevExpress XtraForm. Title: "PHIẾU THU TIỀN".

## 3. Fields
| Label | Control | Editable | Behaviour |
|---|---|---|---|
| Mã bệnh nhân | txtPatient | Not set read-only in the designer | Patient code. Required on save. How it is filled (a lookup, for example) is not in this code. |
| Tổng tiền | txtTotal | No | Sum of Qty x Price over all lines, formatted "n0". |
| Giảm giá | txtDiscount | Yes | Discount amount. Unparseable or empty input is treated as 0. Changing it triggers a recalculation. |
| Phải thu | txtPayable | No | Total - Discount, formatted "n0". |
| Khách đưa | txtTendered | Yes | Cash given by the customer. Unparseable or empty input is treated as 0. Changing it triggers a recalculation. |
| Tiền thối | txtChange | No | Tendered - Payable, formatted "n0". |

Other controls: a context menu item "Xóa dòng" (mnuDeleteRow, delete line). The designer sets only its text and no handler is wired. The line grid is not visible in the source.

## 4. Buttons
- LƯU (btnSave): validate, then save.
- IN PHIẾU (btnPrint): disabled initially. It is enabled after a successful save. It opens frmReceiptPrint as a modal dialog.

## 5. Business rules
### Calculations (Recalc)
1. Total = Σ (line.Qty x line.Price).
2. Payable = Total - Discount.
3. Change = Tendered - Payable.
- Recalc runs only when Discount or Tendered changes. It does NOT run when lines change, so Total is not refreshed by line edits in this code.
- Parsing uses double.TryParse with the current culture. A failed parse gives 0. This is culture dependent, so the thousand and decimal separator behaviour depends on the machine.
- Amounts are stored and computed as double (floating point). A rewrite should use decimal.
- Nothing prevents a discount larger than the total, a negative discount, or tendered less than payable. Change can be negative and is shown as such.

### Validation on Save (in order, stops at first failure)
1. Patient is empty: message "Vui lòng chọn bệnh nhân".
2. No lines: message "Không có dịch vụ để thu".
3. For each line of type Drug, if StockDal.GetStock(code) < Qty: message "Không đủ tồn kho: <code>".
- Service lines have no stock check.
- Tendered is not validated, so a receipt can be saved with insufficient payment.

### Save
1. Create a receipt: PatientCode = text, Discount = parsed discount, Status = "Paid".
2. Id = ReceiptDal.NextId(), which is Max(Id)+1 on tb_Receipt, or 1 if the table is empty.
3. Insert into tb_Receipt (Id, PatientCode, Discount, Status).
4. For each line, ReceiptDal.AttachLine: UPDATE tb_Line SET ReceiptId=@R WHERE Code=@C.
5. Message "Đã lưu phiếu thu", then enable IN PHIẾU.
- Total, Payable, Tendered and Change are NOT persisted. Only the discount is stored.
- Stock is NOT decremented here, although it is checked. Whether this happens elsewhere is unknown.
- No transaction wraps insert and line attach.

### Print
Opens frmReceiptPrint modally. The class is empty in the source and receives no receipt id or data. The print layout and content are not defined here, so this needs follow-up.

## 6. Data
- tb_Receipt(Id, PatientCode, Discount, Status)
- tb_Line(Code, ReceiptId, ...), where lines are pre-existing rows linked to the receipt by Code.
- Enum eStatus {Draft, Paid, Cancelled}. This screen only writes Paid.
- Enum eItemType {Drug, Service}.
- ReceiptDal.SumBetween (sum of Discount for Paid receipts) is used by a report (probably frmTaxReport) and is not part of this screen.

## 7. Open questions, risks and anomalies
1. How the `lines` list is populated is not visible. Nothing in this code adds to it, so as written Save always fails with "Không có dịch vụ để thu". The population logic may be in code not provided, or it is a bug.
2. The DAL SQL commands never bind parameters (@Id, @P, @D, @S, @R, @C). Db.Exec may do it, or the code is incomplete. Confirm before relying on it.
3. AttachLine matches on Code only. This could attach every tb_Line row with that code, including rows from other receipts.
4. NextId (Max+1) is not safe against concurrent users. Ids are double type.
5. Clicking LƯU twice creates duplicate receipts, because the form is not reset or locked after save.
6. Print is not tied to the saved receipt.
7. The "Xóa dòng" menu has no handler. The intended delete-line behaviour is unknown, and it should also refresh the total.
8. Whether Draft or Cancelled receipts are ever created or edited from this screen: no, only Paid is created here. There is no load, edit or cancel flow.
9. Error messages are in Vietnamese and hard-coded. Keep the wording or localise it.
10. Model/Enums.cs is encoded as UTF-16 with a BOM, which may break tooling.
11. The Db, StockDal, Receipt and ReceiptLine definitions were not available. Stock semantics and the line grid need to be read next.

## 8. Rewrite acceptance criteria (derived)
- AC1: Changing Discount or Tendered recomputes Payable and Change, shown with thousands grouping and no decimals.
- AC2: Save is blocked, with the messages above, when there is no patient, no lines, or insufficient stock for a drug line.
- AC3: A successful save persists a receipt with status Paid and the entered discount, links the lines, and enables printing.
- AC4: Print is disabled until a save succeeds.
- AC5: Total, Payable and Change are read-only.
