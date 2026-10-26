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
- Chạy `state.py init` và `inventory.py`, rồi liệt kê số form, user control, báo cáo, SP, timer và menu → form.
- Tạo `APP-OVERVIEW.md` (công nghệ, cấu trúc solution, đề xuất chia module) và khung `NAVIGATION.md`.
- Báo kết quả và mời bạn chỉ màn hình đầu tiên.

**Việc bạn nên làm sau bước này:** đọc nhanh danh sách agent báo và sửa nếu cần: "form X là code chết, bỏ qua", "module này gọi là Y". Các handler không gắn vào menu được báo riêng là `unwired_handlers`, nên hãy cho agent biết nên bỏ qua hay đọc.

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

## 5. Lưu ý và hạn chế

- Các script quét bằng regex, nên là **gợi ý ban đầu**, không đảm bảo đủ. Có thể bỏ sót form mở bằng reflection, menu lưu trong DB, hoặc cách gắn sự kiện lạ. Agent vẫn phải đọc code, và bạn nên đối chiếu độ phủ với những gì bạn biết về app.
- Với DLL đóng, enum nằm trong DLL, hay SP không có script, agent sẽ ghi vào câu hỏi mở và đánh dấu unit `PARTIAL` chứ không đoán.
- Trình bày về y khoa, tài chính, pháp lý luôn là **gợi ý cần chuyên gia xác nhận**.
- Màn hình lớn có thể cần nhiều lượt. Nếu phiên bị ngắt, unit giữ trạng thái `IN_PROGRESS` và phiên sau tự tiếp tục từ điểm dừng.
- Skill này chưa được đánh giá bằng bộ eval. Hiện mới được chạy thử trên một màn hình (`frmPhieuThu`), nên hãy kiểm tra kỹ vài màn hình đầu, nhất là các công thức tính toán và quy tắc thông báo lỗi.

## 6. Quy trình gợi ý cho cả dự án

1. Bootstrap, rồi duyệt danh mục và module.
2. Đọc các **màn hình danh mục** nhỏ trước (ví dụ nhóm `Frm_DM*`) để nắm dữ liệu dùng chung và thuật ngữ.
3. Đọc luồng chính theo thứ tự nghiệp vụ: đăng ký → khám → chỉ định (xét nghiệm, siêu âm) → thu tiền → kho.
4. Sau mỗi 5-10 màn hình: duyệt IMP, trả lời câu hỏi mở, kiểm tra `NAVIGATION.md` và `DATA-MODEL.md`.
5. Cuối cùng chạy bước tổng hợp để có `SRS.md`, rồi đọc lại phần "Known gaps".
