# NAVIGATION
## Startup flow
Program.Main -> frmLogin (btnLogin_Click; the inventory reports its form opening as not wired to a control) -> frmMain (ribbon).
## Menu tree
| Menu caption | Handler | Opens | Unit |
|---|---|---|---|
| PHIẾU THU | btnReceipt_ItemClick | frmReceipt (modeless, single instance) | SCR-REC-Receipt |
| DANH MỤC THUỐC | btnDrug_ItemClick | frmDrug (modal) | PENDING |
| BÁO CÁO THUẾ | btnTax_ItemClick | frmTaxReport (modal) | PENDING |
## Screen-to-screen transitions
| From | To | Trigger | Data passed | Data returned | Condition |
|---|---|---|---|---|---|
| frmMain | SCR-REC-Receipt | menu PHIẾU THU | none | none | one instance only |
| SCR-REC-Receipt | SCR-REC-ReceiptPrint | btnPrint (IN PHIẾU) | none | none (modal) | enabled after save |
## Not reachable from menu
frmLegacyTool (no opener found, unread); `frmLogin.btnLogin_Click` unwired in designer (inventory).
