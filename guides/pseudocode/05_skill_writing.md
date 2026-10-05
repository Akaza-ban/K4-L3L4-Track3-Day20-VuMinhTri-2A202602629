# Hướng dẫn 05 - Viết skill (kỹ năng) cho tác tử

Tài liệu này không phải pseudo-code của chương trình. Đây là quy cách viết một `SKILL.md` ở Phần 3 (viết tay) và tiêu chí đánh giá skill do curator sinh ra ở Phần 4.

## 1. Skill là gì

Skill là một thư mục chứa tệp `SKILL.md` (theo chuẩn Agent Skills) mô tả một **quy trình** (procedure) mà tác tử nên làm theo. Deep Agents nạp skill theo cơ chế nạp dần (progressive disclosure):

1. Khi khởi động, tác tử chỉ thấy `name` và `description` của mọi skill.
2. Khi tác vụ phù hợp, tác tử tự đọc toàn bộ `SKILL.md`.

Hệ quả: `description` quyết định tác tử **có dùng** skill hay không. Phần thân (body) quyết định tác tử **làm gì** khi dùng.

## 2. Cấu trúc thư mục

```text
skills/human/
  <ten-skill>/
    SKILL.md
```

Mỗi thư mục skill phải có `SKILL.md`. Thư mục không có `SKILL.md` bị bỏ qua.

## 3. Định dạng `SKILL.md`

```markdown
---
name: ten-skill
description: Một câu nêu DÙNG KHI NÀO (tình huống kích hoạt).
---

# Tiêu đề ngắn

1. Bước 1 (mệnh lệnh, kiểm chứng được).
2. Bước 2.
3. Điều kiện hoàn thành: ...
```

Ràng buộc kỹ thuật: `name` chỉ gồm chữ thường, số và dấu gạch ngang, tối đa 64 ký tự, trùng tên thư mục; `description` tối đa 1024 ký tự.

## 4. Nguyên tắc viết

| Nguyên tắc | Lý do |
|---|---|
| Nêu **quy trình**, không nêu đáp án | Đáp án của tác vụ học vô ích cho tác vụ mới; chép đáp án là rò rỉ dữ liệu (data leakage). |
| Tổng quát hóa theo **loại lỗi** | Cùng một loại bẫy xuất hiện lại ở tác vụ mới với hình thức khác. |
| Ngắn: tối đa khoảng 40 dòng, 2 đến 3 ý chính | Nghiên cứu SkillsBench ghi nhận skill ngắn và tập trung tốt hơn tài liệu dài. |
| Viết dạng mệnh lệnh và danh sách kiểm tra (checklist) | Mô hình làm theo từng bước dễ hơn đoạn văn mô tả. |
| `description` nêu rõ tình huống kích hoạt | Tác tử chọn skill chỉ dựa vào mô tả. |
| Được nêu tên do **quy ước Acme** yêu cầu (tệp đầu ra như `clean.csv`, `tests/test_regressions.py`, khóa JSON như `meta`, tiêu đề). Không nêu tên tệp dữ liệu, tên hàm, tên cột hay giá trị số **có sẵn trong workspace** của bất kỳ tác vụ nào; ví dụ minh họa dùng tên trung tính (`foo.csv`, `x`) | Dễ quá khớp (overfitting); skill nhắc tên thuộc tác vụ đánh giá bị coi là rò rỉ dữ liệu. |
| `description` nên bắt đầu bằng "Dùng khi ..." và nêu loại tác vụ rộng (phân tích dữ liệu, sửa lỗi mã, phân tích log), không nêu một tác vụ cụ thể | Mô tả quá hẹp khiến tác tử không đọc skill ở tác vụ mới. |

## 5. Ví dụ (miền khác: viết thông điệp commit)

Không tốt:

```markdown
---
name: commit
description: Commit
---
Luôn viết "fix bug in utils.py line 42".
```

Tốt:

```markdown
---
name: write-commit-message
description: Dùng khi chuẩn bị tạo một commit git để thông điệp commit rõ ràng và nhất quán.
---

# Viết thông điệp commit

1. Chạy `git diff --staged` và đọc toàn bộ thay đổi trước khi viết.
2. Dòng đầu tối đa 72 ký tự, ở thể mệnh lệnh ("Add ...", "Fix ..."), nêu NỘI DUNG thay đổi.
3. Nếu thay đổi cần giải thích lý do, thêm một dòng trống và đoạn mô tả TẠI SAO.
4. Không gộp nhiều thay đổi không liên quan vào một commit.
```

## 6. Quy trình gợi ý để rút skill từ một vết thất bại

1. Mở `run.json` của tác vụ học: xem các check thất bại và `detail`.
2. Mở `trace.md`: tìm bước tác tử đáng lẽ phải làm khác (ví dụ không đọc đặc tả, không chạy lại test, không kiểm tra dữ liệu).
3. Viết lại bước đó thành một mệnh lệnh **tổng quát** (không nhắc tên tệp, hàm, số liệu cụ thể).
4. Gộp các mệnh lệnh cùng chủ đề vào một skill; đặt `description` theo tình huống kích hoạt.
5. Chạy lại tác vụ học để xem skill có được tác tử dùng không: cột `skills_read` trong `run.json` lớn hơn 0, và `trace.md` có lệnh `read_file` trên `skills/.../SKILL.md`. Nếu bằng 0, sửa `description`.

## 7. Skill chỉ có tác dụng khi tác tử đọc và làm theo

Thực nghiệm cho thấy hai kiểu thất bại:

1. **Không đọc.** `skills_read` bằng 0: sửa `description` (bắt đầu bằng "Use when ...", nêu loại tác vụ rộng).
2. **Đọc nhưng chỉ làm một phần.** Skill dài 10 quy tắc thường chỉ được áp dụng vài quy tắc, và khi đề bài nói khác (ví dụ "number" so với "số nguyên cent") tác tử có xu hướng làm theo đề. Biện pháp: mỗi quy tắc một dòng, đánh số, dùng từ mệnh lệnh ("MUST"), và kết thúc bằng một danh sách tự kiểm tra tác tử phải rà từng mục trước khi trả lời. Nêu rõ "quy tắc của skill ưu tiên hơn cách hiểu mặc định" khi có xung đột với cách đặt tên hoặc định dạng thông thường.
