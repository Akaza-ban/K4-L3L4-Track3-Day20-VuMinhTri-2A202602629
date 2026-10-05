# Thang điểm (RUBRIC) - 100 điểm

Điểm tối đa 100, cộng thêm tối đa 5 điểm thưởng (tổng không vượt quá 100). Điểm được tính theo nhóm. Số "Phần" khớp với `GUIDE.md`.

## Tổng quan

| # | Hạng mục | Điểm | Cách chấm |
|---|---|---|---|
| 1 | Cài đặt bộ khung (mã nguồn) | 30 | Tự động (`pytest`) |
| 2 | Đường cơ sở và phân loại lỗi (Phần 2) | 12 | Kiểm tra kết quả + đọc báo cáo |
| 3 | Đa tác tử - subagent (Phần 1, 2) | 8 | Kiểm tra kết quả + đọc báo cáo |
| 4 | Skill viết tay (Phần 3) | 10 | Đọc skill + kiểm tra kết quả |
| 5 | Skill tự động - curator (Phần 4) | 10 | Kiểm tra kết quả + đọc báo cáo |
| 6 | Bảng so sánh và quy trình đóng băng (Phần 5) | 10 | `lab.compare` + `scripts/verify_freeze.py` |
| 7 | Báo cáo (Phần 0, 6) | 20 | Đọc báo cáo |
| | **Tổng** | **100** | |
| | Thưởng: thử thách mở rộng (Phần 7) | +5 | Đọc phụ lục |

---

## 1. Cài đặt bộ khung - 30 điểm (tự động)

Chạy `pytest` trên mã nguồn của sinh viên. Điểm mỗi nhóm = điểm tối đa × (số test đạt / tổng số test của tệp).

| Tệp test | Nội dung | Điểm |
|---|---|---|
| `tests/test_02_agent.py` (9 test) | `make_backend` tìm thấy `python` và không lộ khóa API; công cụ tệp và shell dùng chung đường dẫn tương đối; `build_agent` ở hai chế độ; subagent nhận quy ước đường dẫn; nạp skill khi và chỉ khi được yêu cầu; `get_subagents` hợp lệ | 10 |
| `tests/test_03_runner.py` (6 test) | `run_task` ghi bản ghi đầy đủ (gồm `skills_sha256`, `timestamp`); không sửa `tasks/*/workspace`; ghi lỗi thay vì ném ngoại lệ; phát hiện sửa skill; đếm `skills_read` (số skill khác nhau) và `subagent_calls`. Test đếm điều kiện đạt sẵn vì `CONDITIONS` được cung cấp. | 12 |
| `tests/test_04_curator.py` (2 test) | `curate_skills` chỉ ghi skill hợp lệ, không đưa tác vụ đánh giá vào prompt, có đưa phản hồi `detail` của tác vụ học, không cho tên chứa `../`; không gọi mô hình khi không có check thất bại | 8 |

`tests/test_01_provided.py` (12 test) kiểm tra mã có sẵn (gồm `validate_skill`, `parse_skill_blocks`, `compare`), không tính điểm nhưng phải đạt.

Điều kiện: sinh viên không được sửa thư mục `tests/`, `tasks/`, `scripts/` hay các tệp có sẵn (`model.py`, `tasks.py`, `grading.py`, `testing.py`, `compare.py`, hằng số prompt, `render_trace`, `main` của runner, `validate_skill`, `parse_skill_blocks`). Giảng viên chạy test trên bản gốc của các tệp này.

---

## 2. Đường cơ sở và phân loại lỗi - 12 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 2.1 Đủ kết quả `baseline` | 4 | `results/baseline/` có `run.json` và `trace.md` hợp lệ cho cả 6 tác vụ. Thiếu mỗi tác vụ trừ 1 (tối đa 4). |
| 2.2 Bảng phân loại lỗi | 8 | Xem bảng mức độ dưới đây. |

**Mức độ cho 2.2.** Dựa trên các check thất bại của tác vụ học trong kết quả `baseline` (hoặc lần chạy đầu tiên còn lưu).

| Điểm | Mô tả |
|---|---|
| 7 - 8 | Phân loại ít nhất 4 check thất bại; mỗi dòng có bằng chứng cụ thể (tên tác vụ, tên check, trích `detail` hoặc vết); chỉ ra nhóm lỗi chiếm đa số và nguyên nhân chung. Nếu mọi lỗi thuộc cùng một nhóm (thường là nhóm E), nhóm phải nêu bằng chứng phủ định cho các nhóm còn lại, ví dụ số check kỹ thuật đạt/tổng từ `scripts/check_breakdown.py`. |
| 5 - 6 | Phân loại đúng nhưng bằng chứng chung chung hoặc thiếu trích dẫn. |
| 3 - 4 | Liệt kê lỗi nhưng chưa phân nhóm, hoặc phân nhóm sai so với `detail` và vết. |
| 0 - 2 | Thiếu hoặc không dựa trên dữ liệu thực tế. |

Lỗi do hạ tầng (API lỗi, hết thời gian) không được tính là lỗi của tác tử và không dùng làm bằng chứng.

---

## 3. Đa tác tử (subagent) - 8 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 3.1 Thiết kế subagent | 3 | Ít nhất 2 subagent có vai trò khác nhau; `description` nêu rõ khi nào gọi; `system_prompt` có phạm vi rõ ràng. |
| 3.2 Đủ kết quả `subagents` | 2 | `results/subagents/` đủ 6 tác vụ hợp lệ. |
| 3.3 Nhận xét từ số liệu và vết | 3 | Báo cáo mục 5 dựa vào `subagent_calls` và `trace.md`: có giao việc không, subagent nào, thông tin truyền đi đủ hay thiếu, ảnh hưởng đến token. Nếu subagent không được gọi lần nào, giải thích hợp lý vẫn đạt điểm tối đa. |

---

## 4. Skill viết tay - 10 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 4.1 Chất lượng skill | 6 | Tối đa 3 skill; mỗi skill có `description` nêu tình huống kích hoạt; nội dung là quy trình hoặc quy ước tổng quát, ngắn (khoảng 40 dòng trở xuống). Tên do quy ước Acme yêu cầu (tệp đầu ra như `clean.csv`, `tests/test_regressions.py`, khóa JSON, tiêu đề) **được phép** vì chúng là chính quy tắc. Trừ điểm nếu skill chứa tên tệp dữ liệu, tên hàm, tên cột hoặc giá trị số có sẵn trong workspace của bất kỳ tác vụ nào, hoặc đáp án (ví dụ minh họa phải dùng tên trung tính). |
| 4.2 Kết quả chính thức | 4 | `results/skills-human/` đủ 6 tác vụ; `python scripts/verify_freeze.py` không báo lỗi cho điều kiện này. |

Trừ điểm 4.1: skill nhắc tên hoặc nội dung chỉ có ở tác vụ đánh giá (`validate_skill` báo `mentions evaluation material`), mỗi skill trừ 3 (tối thiểu 0). Số vòng phát triển hợp lệ: lần chạy đầu và tối đa 1 lần sửa.

---

## 5. Skill tự động - 10 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 5.1 Curator hoạt động | 4 | `skills/auto/` có ít nhất 1 skill hợp lệ do `python -m lab.curator` sinh ra, không bị sửa tay. |
| 5.2 Đánh giá skill sinh ra | 3 | Báo cáo mục 7 trả lời đủ 3 câu hỏi cho từng skill, có nhận xét dựa trên nội dung thật; nếu xóa skill hoặc chạy lại curator thì ghi lý do. |
| 5.3 Kết quả chính thức | 3 | `results/skills-auto/` đủ 6 tác vụ; `verify_freeze.py` không báo lỗi cho điều kiện này. |

---

## 6. Bảng so sánh và quy trình đóng băng - 10 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 6.1 Bảng so sánh | 5 | `report/table.md` do `lab.compare` sinh ra, khớp với các `run.json` (giảng viên chạy lại `python -m lab.compare` để đối chiếu); đủ 4 cột, 6 hàng tác vụ, các hàng tổng hợp. |
| 6.2 Quy trình đóng băng | 5 | `python scripts/verify_freeze.py` báo OK (có commit `hypotheses` với H1 đến H4 đã điền, đứng trước tag `freeze`; `skills/` không đổi từ tag; mọi lần chạy skill dùng đúng skill đã đóng băng và bắt đầu sau thời điểm tag). |

---

## 7. Báo cáo - 20 điểm

| Tiêu chí | Điểm | Mức đạt đầy đủ |
|---|---|---|
| 7.1 Giả thuyết | 4 | Dự đoán cụ thể, có lý do, có căn cứ từ tài liệu tham khảo; được commit trước tag `freeze`. |
| 7.2 Phân tích kết quả | 8 | Xem bảng mức độ dưới đây. Báo cáo cả điểm tác vụ học ở vòng phát triển và sau đóng băng của cùng bộ skill, dùng chênh lệch làm ước lượng nhiễu. |
| 7.3 Hạn chế và tính hợp lệ | 4 | Nêu và giải thích ít nhất 3 hạn chế (số tác vụ nhỏ, một lần chạy, nhiễu, tác vụ do giảng viên thiết kế, quá khớp, mô hình duy nhất) và ảnh hưởng của từng hạn chế đến kết luận. |
| 7.4 Trình bày và tái lập | 4 | Báo cáo đủ các mục của mẫu, kể cả mục 3 (câu hỏi làm quen Phần 0.3); ghi rõ mô hình, tham số, lệnh chạy, commit; ngôn ngữ kỹ thuật chính xác; có thể tái lập từ README. |

**Mức độ cho 7.2.**

| Điểm | Mô tả |
|---|---|
| 7 - 8 | So sánh điều kiện bằng số liệu, tách tác vụ học và tác vụ đánh giá và tách check kỹ thuật với check quy ước (`rule_`); giải thích cơ chế bằng vết và `skills_read` (skill có được đọc không, có giúp không); phân tích chi phí token; nhận xét về quá khớp hoặc rò rỉ; kết luận khớp với số liệu và không khẳng định quá mức. Kết quả âm hoặc không khác biệt vẫn đạt mức này nếu được phân tích tốt. |
| 5 - 6 | Số liệu đúng và có so sánh, nhưng giải thích cơ chế còn chung chung hoặc thiếu phân tích chi phí. |
| 3 - 4 | Mô tả kết quả nhưng ít diễn giải; kết luận chưa gắn với số liệu. |
| 0 - 2 | Không có phân tích, hoặc kết luận mâu thuẫn với số liệu. |

---

## Thưởng: thử thách mở rộng - tối đa +5

Một hướng trong Phần 7 của `GUIDE.md`, thực hiện đầy đủ và có số liệu. Tiêu chí:

| Tiêu chí | Điểm |
|---|---|
| Thiết kế thí nghiệm rõ ràng, tách biệt khỏi kết quả chính (thư mục kết quả riêng) | +1 |
| Có số liệu so sánh với kết quả chính | +1 |
| Phân tích cơ chế dựa trên vết | +1 |
| Nêu hạn chế và đề xuất bước tiếp theo | +1 |
| Chất lượng mã và khả năng tái lập | +1 |

Điểm thưởng chỉ được tính khi các hạng mục 1 đến 7 đã hoàn thành.

## Trừ điểm

| Vi phạm | Trừ |
|---|---|
| Để lộ khóa API trong kho mã nguồn, vết hoặc báo cáo | -10 |
| Sao chép nội dung tác vụ đánh giá hoặc đáp án vào skill | -10 |
| Sửa `tests/`, `tasks/`, `check.py` hoặc các tệp có sẵn | -10 |
| `verify_freeze.py` báo skill đổi sau tag nhưng báo cáo kết quả như thể không đổi | -10 |
| Kết quả hoặc số liệu trong báo cáo không khớp `results/` | -5 đến -10 |
| Nộp trễ | Theo quy định của lớp |

Việc mở tệp `check.py` hay `run.json` của tác vụ đánh giá trước khi đóng băng không thể kiểm chứng tự động; giảng viên chỉ trừ điểm khi có bằng chứng (ví dụ skill chứa nội dung chỉ có trong tác vụ đánh giá, hoặc lịch sử git).

Nếu có nghi vấn sao chép giữa các nhóm, giảng viên đối chiếu `results/`, `skills/` và báo cáo; bài có nội dung trùng bất thường nhận 0 điểm hạng mục liên quan.

## Quy trình chấm gợi ý cho giảng viên

```bash
git clone <kho-của-nhóm> && cd <kho>
# Chép lại thư mục tests/, tasks/, scripts/ và các tệp có sẵn trong src/lab/ từ kho gốc của giảng viên, rồi:
pip install -e .
pytest                                  # hạng mục 1
python scripts/verify_freeze.py         # hạng mục 4.2, 5.3, 6.2
python -m lab.compare                   # hạng mục 6.1 (so với report/table.md)
python scripts/check_breakdown.py       # hỗ trợ đối chiếu mục 7.2 (kỹ thuật so với quy ước)
```
