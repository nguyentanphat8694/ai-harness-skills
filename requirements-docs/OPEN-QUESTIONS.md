# OPEN-QUESTIONS

| Q-ID | Unit | Question | Why it matters | OPEN/ANSWERED | Answer + date |
|---|---|---|---|---|---|
| Q-001 | SCR-TT-PhieuThu | Where are `etrangthai` and `eLoaiHH` defined (not in any .cs under src; probably a binary DLL)? What are all their values? | Status lifecycles and the "service vs medicine" rule depend on them | OPEN | |
| Q-002 | SCR-TT-PhieuThu | Is editing an issued receipt meant to be possible? `Save()` has a modify branch but `SetModify` disables Save. | Decides whether the rewrite needs an edit-receipt feature | OPEN | |
| Q-003 | SCR-TT-PhieuThu | Is `btSave` ("LƯU ĐĂNG KÝ F2") dead UI copied from the registration form? | Avoid carrying dead UI | OPEN | |
| Q-004 | SCR-TT-PhieuThu | Does `Gioitinh == 0` mean male? (Only inferred from the "Nam" checkbox.) | Gender mapping must be exact | OPEN | |
| Q-005 | SCR-TT-PhieuThu | In view mode (`SetModify`) are Print/Cancel buttons enabled? Code never disables them there, only after `SetNew`. | Confirms intended button states | OPEN | |
