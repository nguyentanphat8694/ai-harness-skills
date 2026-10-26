# APP-OVERVIEW

## Purpose and users
Clinic app (MiniClinic): receipts (PHIẾU THU), drug catalogue, tax report. Users/roles: not yet known (pending; login via `UserDal.Check`, `Session.CurrentUser`).

## Technology
| Aspect | Finding | Evidence |
|---|---|---|
| Language / framework | C# WinForms, .NET Framework (ToolsVersion 14.0) | MiniClinic.csproj |
| UI libraries | DevExpress v16.1 (XtraEditors, XtraBars Ribbon) | MiniClinic.csproj, App/frmMain.cs |
| Data access | Raw `SqlCommand` in DAL classes via helper `Db.Query/Exec` | Model/ReceiptDal.cs |
| Database engine | SQL Server (System.Data.SqlClient); no schema script handed over | Model/ReceiptDal.cs |
| Reporting | frmReceiptPrint, frmTaxReport (not yet read) | inventory |
| Deployment | unknown | |

## Hidden-source findings (important)
- **Missing own-code assembly `Missing.Core`** (`..\libs\Missing.Core.dll`, not in the tree). `Db`, `Session`, `UserDal` are not defined anywhere in the source, so they most likely live in it. Login check, session/permissions and DB access logic are therefore invisible. TODO: ask user for the DLL or its source (or decompile).
- `Model/Enums.cs` is **UTF-16**; raw grep cannot see it. Use `scripts/search_code.py`.
- DevExpress grid/editor config may hold logic (third-party, v16.1).

## Enums (also seed GLOSSARY / DATA-MODEL)
| Enum | Members | File |
|---|---|---|
| `eItemType` | Drug=0, Service=1 | Model/Enums.cs |
| `eStatus` | Draft=0, Paid=1, Cancelled=2 | Model/Enums.cs |
Note: ReceiptDal.SumBetween filters `Status='Paid'` as a string while the enum is numeric; to verify when reading the tax report.

## Solution structure
Single project MiniClinic: `App/` (Program, frmLogin, frmMain), `Forms/` (frmDrug, frmReceipt, frmReceiptPrint, frmTaxReport, frmLegacyTool), `Model/` (Enums, ReceiptDal).

## Architecture
UI forms -> static DAL (ReceiptDal) -> Db helper (in Missing.Core?) -> SQL Server. Tables seen: tb_Receipt, tb_Line; SP sp_RebuildIndexes.

## Actors
| Role | Description | Source |
|---|---|---|
| (unknown) | pending, depends on Missing.Core | |

## Module map (proposed, may change)
| Module | Business capability | Main units | Status |
|---|---|---|---|
| Access | Login, session | frmLogin, frmMain | PENDING |
| Catalogue | Drug list | frmDrug | PENDING |
| Billing | Receipts and printing | frmReceipt, frmReceiptPrint | PENDING |
| Reporting | Tax report | frmTaxReport | PENDING |
| Maintenance | Index rebuild tool | frmLegacyTool (orphan candidate) | PENDING |

## Coverage
0 of 7 screens read (see INDEX.md).
