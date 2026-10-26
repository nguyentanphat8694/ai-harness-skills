# Screen inventory
Depth legend: Inventory = listed only; nothing deeper has been done.

| # | Form | File | Caption | Reached from | Open mode | Status |
|---|------|------|---------|--------------|-----------|--------|
| 1 | frmLogin | App/frmLogin.cs | (no designer provided) | Program.Main | startup | Inventory |
| 2 | frmMain | App/frmMain.cs, .Designer.cs | PHẦN MỀM PHÒNG KHÁM MẪU | frmLogin | modeless | Inventory |
| 3 | frmReceipt | Forms/frmReceipt.cs, .Designer.cs | PHIẾU THU TIỀN | frmMain ribbon "PHIẾU THU" | modeless, single instance | Inventory |
| 4 | frmDrug | Forms/frmDrug.cs | (no designer provided) | frmMain "DANH MỤC THUỐC" | modal | Inventory |
| 5 | frmTaxReport | Forms/frmTaxReport.cs | (no designer provided) | frmMain "BÁO CÁO THUẾ" | modal | Inventory |
| 6 | frmReceiptPrint | Forms/frmReceiptPrint.cs | (none) | frmReceipt "IN PHIẾU" | modal | Inventory - empty stub class, no code |
| 7 | frmLegacyTool | Forms/frmLegacyTool.cs | (none) | NOTHING (comment says unused; confirmed no caller in source) | - | Inventory - likely dead code; has btnFix calling ReceiptDal.RebuildIndex |

Suggested order to review: frmLogin, frmMain, frmReceipt (largest), frmReceiptPrint, frmDrug, frmTaxReport. frmLegacyTool: confirm with user whether to document or exclude.
