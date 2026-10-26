# NAVIGATION

## Startup flow
`frmMain` (ribbon MDI). Login forms `LO010100` / `LO020100` / `LO030100` (login, change password) not yet read. Inventory found 63 forms, 36 user controls, 43 menu bindings.

## Screen-to-screen flows
| From | Trigger | To | Passes | Returns | Condition |
|---|---|---|---|---|---|
| UDSChoThuTien | row double-click | SCR-TT-PhieuThu | `TT010110` via `SetNew` | nothing | row selected |
| UDSDaThu | row double-click | SCR-TT-PhieuThu | `ObPhieuThu` via `SetModify` | nothing | receipt not Đã_hủy, else "Phiếu đã hủy" |
| SCR-TT-PhieuThu | Print | RP020100 | receipt + lines | - | receipt exists |

(Menu tree: see STATE.json `menus`; to be copied here as screens are read.)

## Main ribbon (`frmMain`) -> screens (from inventory)
Real menu buttons (`barButtonItemN` -> `LoadControlX()`): ĐĂNG KÝ KHÁM -> frmDangKy; DANH SÁCH ĐĂNG KÝ -> frmDSDangKy; DANH SÁCH HẸN KHÁM -> frmDSHenKham; QUẢN LÝ NHẬP KHO -> frmNhapkho; DANH SÁCH CHỜ KHÁM / ĐÃ KHÁM -> frmDSChoKham / frmDSDaKham; CHỜ SIÊU ÂM / PHIẾU SIÊU ÂM -> frmDSChoSA / frmDSSieuAm; CHỜ XÉT NGHIỆM / PHIẾU XÉT NGHIỆM -> frmDSChoXN / frmDSPhieuXN; **DANH SÁCH CHỜ THU -> frmDSChoThuTien; DANH SÁCH PHIẾU THU -> frmDSDaThu**; plus 18 catalogue (DM) screens, LỊCH LÀM VIỆC, THIẾT KẾ BÁO CÁO, THAY ĐỔI MẬT KHẨU.

## Unreachable handlers (code never wired to a control)
`btDangKy_ItemClick`, `btBenhAn_ItemClick`, `btThuTien_ItemClick`, `btCDHA_ItemClick` in `frmMain` and `BA000000`, `barButtonItem8_ItemClick` in `BA000000`: no Designer binding found, so treated as dead code. `BA000000` is a near-copy of `frmMain` (same menu captions); confirm whether it is still used.
