# DATA-MODEL
| Table | Columns seen | Keys/relations | Status values | Read/written by | Origin |
|---|---|---|---|---|---|
| `tb_Receipt` | Id (double), PatientCode, Discount, Status | Id = Max+1 | eStatus: Draft, Paid, Cancelled (only Paid written) | SCR-REC-Receipt (R/W); tax report reads Discount where Status='Paid' (ReceiptDal.SumBetween) | inferred (no schema script) |
| `tb_Line` | Code, ReceiptId | linked to receipt by Code (!) | - | SCR-REC-Receipt (W) | inferred |
Stock source: `StockDal.GetStock(code)` (table unknown). SP `sp_RebuildIndexes` called by ReceiptDal.RebuildIndex (caller not found).
