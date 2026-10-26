# modules/TT/MODULE.md
## Module description
Cashier module (Thu tiền): collecting payment for services/medicines ordered for a patient, applying advances, issuing and cancelling receipts. Ribbon form `TT000000` hosts the waiting list and paid list.
## Unit list
| Unit-ID | Type | One-line description |
|---|---|---|
| SCR-TT-PhieuThu | SCR | Receipt form: total, discount, advances, change, save/print/cancel |
| CMP-TT-DSChoThuTien | CMP | Waiting-for-payment list (PENDING) |
| CMP-TT-DSDaThu | CMP | Paid receipts list (PENDING) |
| RPT-TT-PhieuThu | RPT | Receipt print (`RP020100`) (PENDING) |
## Main data entities
`tb_PhieuThu`, `tb_CTChiDinh` (lines, `KeyPT` -> receipt), `tb_TKBenhNhan` (patient advances, `KeyPT` -> receipt).
## Cross-unit business flows
Waiting list (CMP-TT-DSChoThuTien) -> SCR-TT-PhieuThu (new) -> paid list (CMP-TT-DSDaThu) -> SCR-TT-PhieuThu (view/cancel/print).
## Dependencies on other modules
Inventory/stock (`SVC-SHARED-TonKho`), patients (`Customer`), staff lookup, reporting.
