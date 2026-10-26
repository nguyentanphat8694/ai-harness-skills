# Referenced but not present in the provided source
Behaviour that depends on these cannot be documented yet; ask the user for them.
- Missing.Core.dll (..\libs\) - Missing.Core.TaxCalc.Compute(revenue) used by frmTaxReport: tax rules unknown. Needs decompile or source.
- UserDal.Check, Session (login/auth rules)
- DrugDal.Insert, StockDal.GetStock, Db (Query/Exec), entities Receipt, ReceiptLine
- Designer files for frmLogin, frmDrug, frmTaxReport, frmReceiptPrint (control layout/captions); frmReceipt designer lacks control declarations
- frmDrug calls Parse() which is not defined in frmDrug (it is private static in frmReceipt) - source incomplete or does not compile.
- Database schema (tb_Receipt, tb_Line, drug/stock/user tables)
- Report/print layout for receipts
