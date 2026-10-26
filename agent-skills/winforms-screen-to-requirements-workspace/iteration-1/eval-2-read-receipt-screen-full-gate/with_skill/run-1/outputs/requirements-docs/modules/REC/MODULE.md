# REC - Receipts (cashiering)
## Module description
Collecting payment for patients' drugs and services at the counter; used by cashiers.
## Unit list
| Unit-ID | Type | One-line description |
|---|---|---|
| SCR-REC-Receipt | SCR | Payment receipt form: totals, discount, change, save as Paid |
| SCR-REC-ReceiptPrint | SCR | Receipt print form (PENDING, empty in source) |
## Main data entities
`tb_Receipt` (Id, PatientCode, Discount, Status), `tb_Line` (Code, ReceiptId).
## Cross-unit business flows (end to end, by unit ID)
Main menu -> SCR-REC-Receipt -> (save) -> SCR-REC-ReceiptPrint.
## Dependencies on other modules (module -> module, why)
REC -> stock/inventory (StockDal.GetStock, source missing); REC -> patients (PatientCode, no lookup seen); REC -> tax report (frmTaxReport reads Discount of Paid receipts, not yet read).
