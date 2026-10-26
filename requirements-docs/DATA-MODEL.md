# DATA-MODEL

## Entities / tables
| Table | Purpose | Key columns | Status columns | Evidence |
|---|---|---|---|---|
| tb_PhieuThu | Payment receipt | Ma (float), Ngay, NguoiThu, QuayThu, MaBN, TrangThai, TTChung (binary-serialized `ClsTTPhieuThu`: ThanhToan, KHTra), GiamTong | TrangThai: Đã_thu, Đã_hủy | SQL in NTPObPhieuThu.cs (no schema script) |
| tb_CTChiDinh | Ordered service/medicine lines | Ma, MaDV, SL, DG, SLBan, SoGiam, ThanhTien, LoaiHangHoa, KeyPT, TrangThai | TrangThai (values: Q-001) | NTPObCTChiDinh.cs |
| tb_TKBenhNhan | Patient advance payments | ID, MaBN, ThanhTien, KeyPT | Đã_thu, Đã_hạch_toán, Đã_hủy | NTPObTKBenhNhan.cs |
| vw_SLTon | Stock on hand by item | MaDV, SLTon | - | NTPObSLTon.cs |

## Access matrix
| Table | Read by | Written by |
|---|---|---|
| tb_PhieuThu | SCR-TT-PhieuThu, paid list | SCR-TT-PhieuThu |
| tb_CTChiDinh | SCR-TT-PhieuThu | SCR-TT-PhieuThu (KeyPT) |
| tb_TKBenhNhan | SCR-TT-PhieuThu | SCR-TT-PhieuThu |

Note: `TTChung` is stored as a .NET `BinaryFormatter` blob, so it cannot be read or migrated without the original class; flag for the rewrite.
