# OPEN-QUESTIONS.md
| Q-ID | Unit | Question | Why it matters | OPEN/ANSWERED | Answer + date |
|---|---|---|---|---|---|
| Q-001 | SCR-REC-Receipt | Missing source/DLL: StockDal, Db, Receipt, ReceiptLine, Session, UserDal (Missing.Core.dll) | stock rule, DB access and entity shapes unverified | OPEN | |
| Q-002 | SCR-REC-Receipt | How are lines added/edited/deleted ("Xóa dòng"), how is patient picked? | needed to rebuild the screen | OPEN | |
| Q-003 | SCR-REC-Receipt | Does Db.Exec bind the SqlCommand parameters? Real tb_Receipt/tb_Line schema? | persistence correctness | OPEN | |
| Q-004 | SCR-REC-Receipt | Is stock deducted elsewhere after a receipt? | inventory consistency | OPEN | |
| Q-005 | SCR-REC-ReceiptPrint | Required content/layout of the printed receipt (form empty in source) | print requirement | OPEN | |
