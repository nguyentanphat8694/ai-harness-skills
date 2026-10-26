# APP-OVERVIEW
## Purpose and users
Small clinic management app ("PHẦN MỀM PHÒNG KHÁM MẪU" main window): login, drug catalogue, receipts, tax report. Users: clinic staff (roles unknown).
## Technology
| Aspect | Finding | Evidence |
|---|---|---|
| Language / framework | C#, WinForms, .NET Framework (ToolsVersion 14) | MiniClinic.csproj |
| UI libraries | DevExpress v16.1 (XtraEditors, XtraBars Ribbon) | csproj references |
| Data access style / ORM | hand-written DAL with `SqlCommand` | Model/ReceiptDal.cs |
| Database engine | SQL Server (System.Data.SqlClient); no schema script supplied | ReceiptDal.cs |
| Reporting | unknown | - |
| Deployment / installer | unknown | - |
## Hidden-source checks
- Encoding: `Model/Enums.cs` is UTF-16 (invisible to raw grep); read with `search_code.py`.
- Enums extracted (see GLOSSARY): eStatus, eItemType.
- Missing assembly: `Missing.Core` (`..\libs\Missing.Core.dll`), probably own code; classes StockDal, Db, Session, UserDal, Receipt, ReceiptLine not found in source (Q-001).
## Solution structure
App (Program, frmLogin, frmMain), Forms (frmReceipt, frmReceiptPrint, frmDrug, frmTaxReport, frmLegacyTool), Model (ReceiptDal, Enums).
## Architecture
Forms call static DAL classes directly; no BLL layer seen.
## Actors
| Role | Description | Source |
|---|---|---|
| Logged-in user | single role seen; no permission checks found so far | App/frmLogin.cs |
## Module map
| Module | Business capability | Main units | Status |
|---|---|---|---|
| REC | Receipts / cashiering | SCR-REC-Receipt, SCR-REC-ReceiptPrint | 1 PARTIAL, 1 PENDING |
## Coverage
See INDEX.md. Unread: frmLogin, frmMain, frmDrug, frmTaxReport, frmLegacyTool (not opened from menu: orphan candidate, unreviewed).
