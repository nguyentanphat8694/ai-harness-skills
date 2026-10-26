# Software Requirements Specification

_Assembled 2026-10-26 from requirements-docs. Rebuild with scripts/build_srs.py._

<!-- manual:start -->
(Add business context, decisions and legacy differences here.)
<!-- manual:end -->

## 1. Application overview

_Missing: APP-OVERVIEW.md_

## 2. Navigation and screen flows


#### Startup flow
`frmMain` (ribbon MDI). Login forms `LO010100` / `LO020100` / `LO030100` (login, change password) not yet read. Inventory found 63 forms, 36 user controls, 43 menu bindings.

#### Screen-to-screen flows
| From | Trigger | To | Passes | Returns | Condition |
|---|---|---|---|---|---|
| UDSChoThuTien | row double-click | SCR-TT-PhieuThu | `TT010110` via `SetNew` | nothing | row selected |
| UDSDaThu | row double-click | SCR-TT-PhieuThu | `ObPhieuThu` via `SetModify` | nothing | receipt not Đã_hủy, else "Phiếu đã hủy" |
| SCR-TT-PhieuThu | Print | RP020100 | receipt + lines | - | receipt exists |

(Menu tree: see STATE.json `menus`; to be copied here as screens are read.)


## 3. Roles and permissions

_Missing: ROLES-MATRIX.md_

## 4. Data model


#### Entities / tables
| Table | Purpose | Key columns | Status columns | Evidence |
|---|---|---|---|---|
| tb_PhieuThu | Payment receipt | Ma (float), Ngay, NguoiThu, QuayThu, MaBN, TrangThai, TTChung (binary-serialized `ClsTTPhieuThu`: ThanhToan, KHTra), GiamTong | TrangThai: Đã_thu, Đã_hủy | SQL in NTPObPhieuThu.cs (no schema script) |
| tb_CTChiDinh | Ordered service/medicine lines | Ma, MaDV, SL, DG, SLBan, SoGiam, ThanhTien, LoaiHangHoa, KeyPT, TrangThai | TrangThai (values: Q-001) | NTPObCTChiDinh.cs |
| tb_TKBenhNhan | Patient advance payments | ID, MaBN, ThanhTien, KeyPT | Đã_thu, Đã_hạch_toán, Đã_hủy | NTPObTKBenhNhan.cs |
| vw_SLTon | Stock on hand by item | MaDV, SLTon | - | NTPObSLTon.cs |

#### Access matrix
| Table | Read by | Written by |
|---|---|---|
| tb_PhieuThu | SCR-TT-PhieuThu, paid list | SCR-TT-PhieuThu |
| tb_CTChiDinh | SCR-TT-PhieuThu | SCR-TT-PhieuThu (KeyPT) |
| tb_TKBenhNhan | SCR-TT-PhieuThu | SCR-TT-PhieuThu |

Note: `TTChung` is stored as a .NET `BinaryFormatter` blob, so it cannot be read or migrated without the original class; flag for the rewrite.


## 5. Configuration and integrations

_Missing: CONFIG-AND-INTEGRATIONS.md_

## 6. End-to-end workflows

_Missing: WORKFLOWS.md_

## 7. Characteristic business functions


| FN-ID | Business name | Module | Owner unit | Used by | Input -> Output | Assessment |
|---|---|---|---|---|---|---|
| FN-TT-001 | Total cost | TT | SCR-TT-PhieuThu | - | lines (SL, DG) -> Σ SL×DG | Suspect (IMP-TT-002) |
| FN-TT-002 | Amount to pay | TT | SCR-TT-PhieuThu | - | total, discount, advance -> total − discount − advance | Suspect (IMP-TT-002) |
| FN-TT-003 | Change due | TT | SCR-TT-PhieuThu | - | tendered, payable -> tendered − payable | OK |


## 8. Improvements


| IMP-ID | Title | Applies to | Type | Severity | Status | Resulting REQ |
|---|---|---|---|---|---|---|
| IMP-TT-001 | Receipt number can collide under concurrent cashiers | REQ-006, BR-006 | Concurrency | High | PROPOSED | |
| IMP-TT-002 | Totals ignore line discounts and go stale after row delete | REQ-004, REQ-009, FN-001/002 | Logic error | High | PROPOSED | |
| IMP-TT-005 | Save is not atomic | REQ-006 | Data-integrity risk | High | PROPOSED | |
| IMP-TT-003 | Stock check uses in-memory cache | REQ-005 | Data-integrity risk | Medium | PROPOSED | |
| IMP-TT-004 | No role check for collect/cancel | REQ-001, REQ-007 | Security/permissions | Medium | PROPOSED | |
| IMP-TT-006 | No validation of amounts | REQ-004, REQ-006 | Missing validation | Medium | PROPOSED | |


## 9. Open questions


| Q-ID | Unit | Question | Why it matters | OPEN/ANSWERED | Answer + date |
|---|---|---|---|---|---|
| Q-001 | SCR-TT-PhieuThu | Where are `etrangthai` and `eLoaiHH` defined (not in any .cs under src; probably a binary DLL)? What are all their values? | Status lifecycles and the "service vs medicine" rule depend on them | OPEN | |
| Q-002 | SCR-TT-PhieuThu | Is editing an issued receipt meant to be possible? `Save()` has a modify branch but `SetModify` disables Save. | Decides whether the rewrite needs an edit-receipt feature | OPEN | |
| Q-003 | SCR-TT-PhieuThu | Is `btSave` ("LƯU ĐĂNG KÝ F2") dead UI copied from the registration form? | Avoid carrying dead UI | OPEN | |
| Q-004 | SCR-TT-PhieuThu | Does `Gioitinh == 0` mean male? (Only inferred from the "Nam" checkbox.) | Gender mapping must be exact | OPEN | |
| Q-005 | SCR-TT-PhieuThu | In view mode (`SetModify`) are Print/Cancel buttons enabled? Code never disables them there, only after `SetNew`. | Confirms intended button states | OPEN | |


## 10. Glossary

_Missing: GLOSSARY.md_

## 11. Requirements by module

### Module TT

See [TT module description](modules/TT/MODULE.md).

| Unit | Status | Document |
|---|---|---|
| CMP-TT-DSChoThuTien | PENDING | [CMP-TT-DSChoThuTien.md](modules/TT/units/CMP-TT-DSChoThuTien.md) |
| CMP-TT-DSDaThu | PENDING | [CMP-TT-DSDaThu.md](modules/TT/units/CMP-TT-DSDaThu.md) |
| RPT-TT-PhieuThu | PENDING | [RPT-TT-PhieuThu.md](modules/TT/units/RPT-TT-PhieuThu.md) |
| SCR-TT-PhieuThu | DONE | [SCR-TT-PhieuThu.md](modules/TT/units/SCR-TT-PhieuThu.md) |

### Module SHARED

| Unit | Status | Document |
|---|---|---|
| SVC-SHARED-TonKho | PENDING | [SVC-SHARED-TonKho.md](modules/SHARED/units/SVC-SHARED-TonKho.md) |

## 12. Known gaps at assembly time

- APP-OVERVIEW.md missing or empty
- ROLES-MATRIX.md missing or empty
- CONFIG-AND-INTEGRATIONS.md missing or empty
- WORKFLOWS.md missing or empty
- GLOSSARY.md missing or empty
- CMP-TT-DSChoThuTien is PENDING
- CMP-TT-DSDaThu is PENDING
- RPT-TT-PhieuThu is PENDING
- SVC-SHARED-TonKho is PENDING
- inventory item SCR:frmKey has no unit
- inventory item SCR:LO030100 has no unit
- inventory item SCR:LO010100 has no unit
- inventory item SCR:LO020100 has no unit
- inventory item SCR:frmMain has no unit
- inventory item SCR:CD020100 has no unit
- inventory item SCR:frmDSChoTH has no unit
- inventory item SCR:CD010100 has no unit
- inventory item SCR:frmDSSieuAm has no unit
- inventory item CMP:USA2 has no unit
- inventory item CMP:USANew has no unit
- inventory item SCR:frmDSChoSA has no unit
- inventory item CMP:WebCamCapture has no unit
- inventory item SCR:SA000000 has no unit
- inventory item CMP:USieuAm has no unit
- inventory item CMP:UChoSA has no unit
- inventory item SCR:frmSieuAm has no unit
- inventory item CMP:UMainSA has no unit
- inventory item SCR:FrmChuyenDichVu has no unit
- inventory item CMP:UNewCapture has no unit
- inventory item CMP:USA_Capture has no unit
- inventory item SCR:FrmTamUng has no unit
- inventory item CMP:ULichLamViec has no unit
- inventory item SCR:FrmChucNangLLV has no unit
- inventory item CMP:UNgay has no unit
- inventory item SCR:frmLichLamViec has no unit
- inventory item SCR:FormCommon has no unit
- inventory item SCR:frmDSPhieuXN has no unit
- inventory item CMP:UDSPhieuXN has no unit
- inventory item CMP:UPhieuXetNghiem has no unit
- inventory item SCR:frmPhieuXetNghiem has no unit
- inventory item CMP:UDSChoXN has no unit
- inventory item SCR:frmDSChoXN has no unit
- inventory item SCR:XN000000 has no unit
- inventory item SCR:FrmQLyXetNghiemSimple has no unit
- inventory item CMP:UTKSuDungThuoc has no unit
- inventory item CMP:UTKKhamBenh has no unit
- inventory item SCR:frmTKKhamBenh has no unit
- inventory item SCR:Frm_DMDichVu has no unit
- inventory item SCR:Frm_DMThuoc has no unit
- inventory item SCR:Frm_DMXetNghiem has no unit
- inventory item SCR:Frm_DMUser has no unit
- inventory item SCR:Frm_DMTSo has no unit
- inventory item SCR:BN020100 has no unit
- inventory item SCR:Frm_DMQuan has no unit
- inventory item SCR:Frm_DMPK has no unit
- inventory item SCR:Frm_DMDonVi has no unit
- inventory item SCR:frmText has no unit
- inventory item SCR:Frm_DMKho has no unit
- inventory item SCR:Frm_DMUser_Nhom has no unit
- inventory item SCR:Frm_DMNhanSu has no unit
- inventory item SCR:Frm_DMTinh has no unit
- inventory item SCR:Frm_DMNhomXetNghiem has no unit
- inventory item SCR:Frm_DMNhomDichVu has no unit
- inventory item SCR:Frm_DMLK has no unit
- inventory item SCR:Frm_DMMau has no unit
- inventory item SCR:Frm_DMNgheNghiep has no unit
- inventory item SCR:Frm_DMICD has no unit
- inventory item SCR:BN010100 has no unit
- inventory item CMP:UDSChoKham has no unit
- inventory item SCR:frmDSChoKham has no unit
- inventory item SCR:FrmPhieuKhamChung has no unit
- inventory item CMP:UDaKham has no unit
- inventory item SCR:frmDSDaKham has no unit
- inventory item SCR:frmBenhAn has no unit
- inventory item SCR:FrmMainBenhAn has no unit
- inventory item SCR:BA000000 has no unit
- inventory item CMP:UChoKham has no unit
- inventory item CMP:UNhatKy has no unit
- inventory item CMP:UDichVuUtils has no unit
- inventory item CMP:UImages has no unit
- inventory item CMP:TI010100 has no unit
- inventory item CMP:UD010100 has no unit
- inventory item CMP:UImage has no unit
- inventory item CMP:UT010100 has no unit
- inventory item CMP:UGoTat has no unit
- inventory item CMP:UTimBN has no unit
- inventory item CMP:UHenKham has no unit
- inventory item CMP:UMauBA has no unit
- inventory item SCR:RP010100 has no unit
- inventory item SCR:frmDSChoThuTien has no unit
- inventory item CMP:UDSDaThu has no unit
- inventory item CMP:UMainThuTien has no unit
- inventory item SCR:TT000000 has no unit
- inventory item CMP:UDSChoThuTien has no unit
- inventory item SCR:frmDSDaThu has no unit
- inventory item CMP:UNhapKho has no unit
- inventory item SCR:frmNhapkho has no unit
- inventory item SCR:FrmBCTonKho has no unit
- inventory item SCR:frmDSHenKham has no unit
- inventory item SCR:FrmMainDangKy has no unit
- inventory item SCR:frmDangKy has no unit
- inventory item CMP:UDangKy has no unit
- inventory item SCR:DK000000 has no unit
- inventory item SCR:frmDSDangKy has no unit
- inventory item CMP:UDSDangKy has no unit
- inventory item SCR:FrmCapNhatNo has no unit
- inventory item CMP:UBenhNhan has no unit
