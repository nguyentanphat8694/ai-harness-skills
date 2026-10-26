# WORKFLOWS
## Counter payment
Login -> main menu PHIẾU THU -> SCR-REC-Receipt (enter patient, lines, discount, cash) -> LƯU: receipt `tb_Receipt` status Paid, lines linked -> IN PHIẾU -> SCR-REC-ReceiptPrint. Exceptional: stock shortage, no patient, no lines abort the save. Upstream steps (registration, prescribing) not yet read.
