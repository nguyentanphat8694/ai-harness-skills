# NAVIGATION

## Startup flow
`Program.Main` -> `Application.Run(new frmLogin())` (App/Program.cs) -> btnLogin_Click validates non-empty fields, `UserDal.Check` -> `new frmMain().Show()`, login hidden (App/frmLogin.cs). No version/DB checks seen.
Note: btnLogin_Click is reported as an unwired handler (Designer for frmLogin not in tree); presumably wired at runtime or in a missing file. Pending (SCR frmLogin).

## Menu tree (frmMain ribbon)
| Menu path | Caption | Opens (unit) | Visible when (role/condition) |
|---|---|---|---|
| Ribbon | PHIẾU THU (Receipt) | frmReceipt, single instance, modeless - PENDING | unknown |
| Ribbon | DANH MỤC THUỐC (Drug catalogue) | frmDrug, modal - PENDING | unknown |
| Ribbon | BÁO CÁO THUẾ (Tax report) | frmTaxReport, modal - PENDING | unknown |

## Screen-to-screen flows
| From | Trigger | To | Passes | Returns | Condition |
|---|---|---|---|---|---|
| frmLogin | btnLogin_Click | frmMain | Session.CurrentUser | - | credentials valid |
| frmReceipt | btnPrint (IN PHIẾU) | frmReceiptPrint | pending | pending | pending |

## Unreachable from menu
- frmLegacyTool: no menu or file opens it (comment: "Old maintenance tool"); calls sp_RebuildIndexes. Orphan candidate, awaiting user confirmation.
