# FUNCTIONS.md
| FN-ID | Business name | Module | Owner unit | Used by | Input -> Output | Assessment |
|---|---|---|---|---|---|---|
| FN-REC-001 | Receipt total | REC | SCR-REC-Receipt | SCR-REC-Receipt | lines -> sum(Qty*Price) | Suspect |
| FN-REC-002 | Amount due | REC | SCR-REC-Receipt | SCR-REC-Receipt | total, discount -> total - discount | Suspect |
| FN-REC-003 | Change | REC | SCR-REC-Receipt | SCR-REC-Receipt | cash given, due -> given - due | Suspect |
