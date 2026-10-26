# Hướng dẫn dùng skill `winforms-screen-to-requirements`

Skill biến source WinForms cũ thành bộ tài liệu requirement cho cả app, đọc từng màn hình theo yêu cầu của bạn. Kết quả nằm trong thư mục `requirements-docs/`.

## 0. Chuẩn bị (làm một lần)

1. **Đặt skill ở nơi agent tìm thấy.** Skill hiện nằm ở `agent-skills/winforms-screen-to-requirements/`. Muốn agent tự nhận skill, chép hoặc tạo symlink thư mục này vào nơi harness của bạn đọc skill, ví dụ `.claude/skills/` (theo project) hoặc `~/.claude/skills/` (toàn máy). Skill-creator trong repo này nằm ở `.agents/skills/`, nên nếu harness của bạn dùng thư mục đó thì đặt cùng chỗ.
2. **Cần Python 3** (chỉ dùng thư viện chuẩn, không cần cài thêm).
3. **Đặt source** ở một thư mục agent đọc được. Ví dụ `src/` cạnh thư mục làm việc.
4. **Mở agent ngay tại thư mục chứa source** (hoặc thư mục cha của nó), để `requirements-docs/` được tạo cạnh source.
5. Nếu có **script SQL / backup DB** (bảng, stored procedure), để cạnh source. Có thì tài liệu data model sẽ chính xác hơn, không có thì agent chỉ suy ra bảng từ code.

## 1. Lần đầu sử dụng (bootstrap)

Gửi một prompt như sau:

```
Dùng skill winforms-screen-to-requirements. Source WinForms cũ của app nằm ở ./src.
Hãy bootstrap: quét toàn bộ source, lập danh mục màn hình, tạo requirements-docs.
Tài liệu viết bằng tiếng Việt. Chưa đọc sâu màn hình nào, tôi sẽ chỉ từng màn hình sau.
```

(Bỏ câu "tiếng Việt" nếu bạn muốn tài liệu tiếng Anh, là mặc định.)

Agent sẽ:
- Chạy `state.py init` và `inventory.py`, rồi liệt kê số form, user control, báo cáo, SP, timer, menu → form và form khởi động (`Application.Run`).
- Kiểm tra **nguồn bị ẩn** (xem mục 5): file mã hóa UTF-16 / code page cũ, toàn bộ enum, assembly tham chiếu nhưng thiếu file.
- Đề xuất các form **orphan** (không menu nào mở, không file nào nhắc tới) để bạn xác nhận.
- Tạo `APP-OVERVIEW.md` (công nghệ, cấu trúc solution, đề xuất chia module) và khung `NAVIGATION.md`.
- Báo kết quả và mời bạn chỉ màn hình đầu tiên.

**Việc bạn nên làm sau bước này:**
- Đọc danh sách và sửa nếu cần: "module này gọi là Y", "form X là code chết, bỏ qua".
- Với từng đề xuất orphan, trả lời đúng/sai. Menu dựng từ bảng DB hoặc reflection có thể khiến một form đang dùng bị nhầm là orphan.
- Nếu agent báo thiếu DLL hoặc source của thư viện tự viết, gửi một lần cho đủ (xem mục 5).

## 2. Đưa từng màn hình cho agent (vòng lặp chính)

Có 3 cách chỉ màn hình, theo thứ tự agent nhận diện chính xác nhất:

**Cách A: gửi ảnh chụp màn hình (khuyên dùng).**
```
[đính kèm ảnh]
Đọc màn hình này, dùng skill winforms-screen-to-requirements.
```
Agent đọc các chữ trong ảnh (tiêu đề, nhãn, nút, tiêu đề cột), tìm form trong source, rồi đối chiếu ảnh với code để phát hiện control ẩn/hiện theo quyền hoặc trạng thái.

**Cách B: nói tên menu hoặc caption.**
```
Đọc màn hình "Phiếu thu tiền" (menu Thu tiền → Danh sách phiếu thu).
```

**Cách C: nói tên form/class.**
```
Đọc form frmPhieuThu.
```

Agent sẽ nêu giả định nếu có nhiều form khớp, đọc xuống tận DB/báo cáo, viết spec vào `modules/<MODULE>/units/`, rồi báo cáo ngắn gồm: unit tìm được, số requirement/rule/hàm tính, phát hiện đáng chú ý, gợi ý cải tiến, màn hình nên đọc tiếp và độ phủ (ví dụ "14/99").

Mỗi lần chỉ nên đưa **một** màn hình, để kết quả đủ sâu và bạn kiểm tra được.

## 3. Các prompt dùng tiếp ở các phiên sau

Mở phiên mới và nhắc skill. Agent tự đọc `requirements-docs/STATE.json` nên nhớ được việc đã làm, bạn không cần dán lại ngữ cảnh.

| Bạn muốn | Prompt mẫu |
|---|---|
| Đọc màn hình tiếp | `Tiếp tục dự án requirements-docs. Đọc màn hình này [ảnh]` |
| Xem còn gì chưa đọc | `Còn màn hình nào chưa đọc? Độ phủ hiện tại bao nhiêu? Gợi ý 3 màn hình nên đọc tiếp.` |
| Đọc màn hình phụ thuộc đang chờ | `Đọc tiếp các unit PENDING mà SCR-TT-PhieuThu phụ thuộc.` |
| Hỏi lại màn hình đã đọc | `Màn hình phiếu thu tính số tiền thanh toán thế nào?` (agent trả lời từ tài liệu, không đọc lại source) |
| Thêm yêu cầu cho app mới | `Ở app mới, phiếu thu phải chặn giảm giá lớn hơn tổng tiền.` |
| Sửa yêu cầu | `Ở phiếu thu, số phiếu dùng sequence của DB thay vì Max+1.` |
| Bỏ chức năng | `App mới bỏ nút In phiếu thu trên form này.` |
| Duyệt gợi ý cải tiến | `Chấp nhận IMP-TT-001 và IMP-TT-005. Từ chối IMP-TT-004 vì app chỉ có một thu ngân.` |
| Trả lời câu hỏi mở | `Q-004: Gioitinh = 0 là Nam.` |
| Source đã đổi | `Source đã được cập nhật, kiểm tra màn hình nào bị ảnh hưởng.` (agent chạy `check`, đánh dấu STALE và đọc lại phần đổi) |
| Hỏi về enum / hằng số | `Enum etrangthai có những giá trị nào, nằm ở đâu?` (agent dùng `search_code.py` / `enums.py`, không dùng grep thô) |
| Chốt form chết | `Đánh dấu orphan cho frmOld và frmTool, bỏ frmDemo ra khỏi phạm vi.` |
| Gửi thư viện còn thiếu | `Đây là Missing.Core.dll, của chúng tôi. Đọc logic tính thuế trong đó.` |
| Rà từng nhóm | `Liệt kê tất cả IMP mức Cao đang PROPOSED.` / `Liệt kê câu hỏi mở theo màn hình.` |
| Tổng hợp cuối | `Tôi đã đọc đủ. Còn thiếu gì? Dựng SRS.md cuối cùng.` |

**Mẹo viết prompt**
- Luôn nêu tên skill ở đầu phiên, vì đó là cách chắc nhất để skill được kích hoạt.
- Nhắc mã ID (`REQ-…`, `IMP-…`, `Q-…`, `SCR-…`), vì agent tra được ngay.
- Phát biểu thay đổi cho app mới thật cụ thể (điều kiện, ngưỡng, thông báo), vì mỗi yêu cầu phải có tiêu chí chấp nhận kiểm chứng được.

## 4. Cách tài liệu được tạo ra

```
requirements-docs/
├── STATE.json     trạng thái, hash, bộ đếm ID (do script quản lý, đừng sửa tay)
├── INDEX.md       bảng tổng hợp, độ phủ (sinh tự động, đừng sửa tay)
├── APP-OVERVIEW.md  NAVIGATION.md  DATA-MODEL.md  ROLES-MATRIX.md  CONFIG-AND-INTEGRATIONS.md  WORKFLOWS.md
├── FUNCTIONS.md   các hàm tự tính (công thức, ca biên, test vector)
├── IMPROVEMENTS.md  chỗ chưa hợp lý của app cũ + gợi ý (tách riêng khỏi requirement)
├── OPEN-QUESTIONS.md  GLOSSARY.md  CHANGELOG.md
├── SRS.md         tài liệu tổng hợp cuối
└── modules/<MODULE>/units/<UNIT-ID>.md   spec chi tiết từng màn hình/dịch vụ
```

Quy tắc cần nhớ:
- Mô tả của app cũ (`LEGACY`) được **giữ nguyên**; yêu cầu mới hoặc thay đổi nằm riêng (`NEW` / `CHANGED`).
- Gợi ý cải tiến **không** tự áp vào requirement. Bạn chấp nhận hoặc từ chối.
- Muốn tự ghi chú trong tài liệu mà không bị agent ghi đè, đặt giữa `<!-- manual:start -->` và `<!-- manual:end -->`.
- Đừng sửa `STATE.json` và `INDEX.md` bằng tay.

## 5. Nguồn bị ẩn: mã hóa, enum, DLL, orphan

Đây là những chỗ dễ làm tài liệu thiếu mà không ai biết. Skill có sẵn công cụ cho từng chỗ.

| Vấn đề | Công cụ | Ghi chú |
|---|---|---|
| Tìm code bị `grep` bỏ sót vì file là UTF-16 hoặc code page cũ | `scripts/search_code.py` | `--fold` bỏ qua hoa thường và dấu, `-C N` xem các dòng sau, `--list-encodings` liệt kê file `grep` thô không đọc được. **Kết quả rỗng của `grep` không phải bằng chứng là không có.** |
| Enum, trạng thái, danh sách quyền, tên bảng | `scripts/enums.py --md` | Kết quả được đưa vào `GLOSSARY.md`, `DATA-MODEL.md`, `ROLES-MATRIX.md` |
| Thư viện tham chiếu nhưng thiếu file, DLL tự viết | `scripts/assemblies.py` | Phân loại: bên thứ ba / dự án trong solution / có thể là code của nhóm. File thiếu được hỏi bạn một lần cho tất cả |
| Logic nằm trong DLL của nhóm | `references/decompile.md` | Agent ưu tiên xin source. Chỉ decompile DLL của chính chủ app, kết quả đặt ngoài cây source và ghi độ tin cậy là "suy luận" |
| Form chết | `state.py flag` | `--auto-orphans` đề xuất theo mức tin cậy (cao/trung bình/thấp), `--apply` chỉ áp dụng mức cao, `flag TYPE:Class --note "lý do"` đánh dấu từng mục, `--skip "lý do"` loại khỏi phạm vi, `--clear` hoàn tác |

Orphan và mục bị loại khỏi phạm vi **không** tính vào mẫu số độ phủ, nhưng vẫn liệt kê trong `INDEX.md` nên không bị che giấu. Sau vài màn hình nên chạy lại `--auto-orphans`, vì một tham chiếu mới có thể đưa form ra khỏi trạng thái orphan.

Nếu thiếu thư viện hoặc logic nằm trong binary không lấy được, agent **không đoán**: nó ghi câu hỏi mở, đánh dấu unit `PARTIAL` và chỉ rõ vị trí gọi (`file:hàm:dòng`).

## 6. Lưu ý và hạn chế

- Các script quét bằng regex, nên là **gợi ý ban đầu**, không đảm bảo đủ. Có thể bỏ sót form mở bằng reflection, menu lưu trong DB, hoặc cách gắn sự kiện lạ. Agent vẫn phải đọc code, và bạn nên đối chiếu độ phủ với những gì bạn biết về app.
- Regex thiên về C#. VB.NET mới được hỗ trợ ở mức cơ bản (ví dụ trích enum), chưa kiểm thử với source VB thật.
- Việc decompile chưa được thử trên DLL thật. Nếu máy chưa có `ilspycmd`, agent sẽ nhờ bạn cài, không tự cài.
- Trình bày về y khoa, tài chính, pháp lý luôn là **gợi ý cần chuyên gia xác nhận**.
- Màn hình lớn có thể cần nhiều lượt. Nếu phiên bị ngắt, unit giữ trạng thái `IN_PROGRESS` và phiên sau tự tiếp tục từ điểm dừng.
- Bộ eval (mục 7) đã có tiêu chí nhưng **chưa được chạy bằng agent**; phần cơ học đã được thử bằng script trên app mẫu và trên một màn hình thật (`frmPhieuThu`). Hãy kiểm tra kỹ vài màn hình đầu, nhất là các công thức tính toán và quy tắc thông báo lỗi.

## 7. Kiểm thử skill (evals)

`evals/evals.json` có 8 kịch bản và 54 tiêu chí kiểm chứng được, chạy trên một app mẫu nhỏ có sẵn trong `evals/files/mini-clinic/` (7 form). App mẫu cố ý gài các "bẫy" thật: enum nằm trong file UTF-16, một DLL được tham chiếu nhưng thiếu, một form chết, menu mở form qua hàm trung gian, và một hàm trả về 0 mà không chạy truy vấn.

| # | Kịch bản | Kiểm tra gì |
|---|---|---|
| 1 | Bootstrap | inventory, form khởi động, menu qua hàm trung gian, UTF-16, DLL thiếu, orphan, chưa đọc sâu màn hình nào |
| 2 | Đọc màn hình phiếu thu | nhận diện từ chuỗi trên ảnh, FN có test vector, thứ tự validate, thông báo, IMP tách riêng, cổng kiểm tra |
| 3 | Enum trong file UTF-16 | tìm đúng enum, không kết luận "nằm trong DLL", ghi các trạng thái không bao giờ được gán |
| 4 | Logic nằm trong DLL thiếu | unit `PARTIAL`, không bịa công thức thuế, tìm ra hàm trả về 0 sai |
| 5 | Thêm yêu cầu mới / bỏ chức năng | giữ nguyên LEGACY, REQ mới có tiêu chí chấp nhận, `DROPPED`, CHANGELOG |
| 6 | Độ phủ và orphan | đề xuất orphan kèm lưu ý, mẫu số độ phủ, gợi ý màn hình tiếp theo |
| 7 | Source thay đổi | phát hiện drift qua hash, `STALE`, chỉ đọc lại phần đổi |
| 8 | Không nên kích hoạt | yêu cầu viết code login bình thường, skill không được dùng |

Cách chạy: dùng skill-creator (`.agents/skills/skill-creator`), chạy từng eval với và không có skill, chấm các tiêu chí rồi xem kết quả bằng `eval-viewer`. Các eval 2, 4, 5, 6, 7 cần dựng trạng thái từ bước trước (ghi ở trường `setup`). Có thể chạy `scripts/*.py` trực tiếp trên `evals/files/mini-clinic` để tự kiểm tra phần cơ học trước.

Các tiêu chí đo hành vi quan sát được trong tài liệu và `STATE.json`. Hai việc cần bạn tự đánh giá thủ công: tài liệu có thật sự đủ để viết lại app không, và các gợi ý IMP có hợp lý về nghiệp vụ không.

## 8. Quy trình gợi ý cho cả dự án

1. Bootstrap, rồi duyệt danh mục, module, orphan, danh sách enum và thư viện thiếu.
2. Đọc các **màn hình danh mục** nhỏ trước (ví dụ nhóm `Frm_DM*`) để nắm dữ liệu dùng chung và thuật ngữ.
3. Đọc luồng chính theo thứ tự nghiệp vụ: đăng ký → khám → chỉ định (xét nghiệm, siêu âm) → thu tiền → kho.
4. Sau mỗi 5-10 màn hình: duyệt IMP, trả lời câu hỏi mở, kiểm tra `NAVIGATION.md` và `DATA-MODEL.md`.
5. Cuối cùng chạy bước tổng hợp để có `SRS.md`, rồi đọc lại phần "Known gaps".
