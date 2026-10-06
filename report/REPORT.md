# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Vũ Minh Trí | 2A202602629 | 100% |

- Mô hình: `deepseek:deepseek-chat` (`LAB_MODEL=deepseek:deepseek-chat`), nhiệt độ: `0` (`LAB_TEMPERATURE=0`), `recursion_limit`: `120`
- Phiên bản Deep Agents: `deepagents 0.7.21`, hệ điều hành: Windows 11, chạy trực tiếp trong môi trường ảo `.venv` (Python 3.11)
- Số lần chạy tác vụ đã dùng / ngân sách: 9 lần chạy tập học, tiếp tục chạy tập đánh giá sau đóng băng
- Commit của tag `freeze`: (cập nhật sau khi gán tag)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán subagents sẽ đạt điểm tương đương hoặc cao hơn baseline trên các tác vụ kỹ thuật phức tạp (như code-eval) nhờ phân rã công việc cho các vai trò chuyên biệt (explorer tìm kiếm thông tin, reviewer kiểm thử độc lập), tuy nhiên chi phí token sẽ cao hơn khoảng 10-25% do việc sinh prompt và trao đổi ngữ cảnh phân việc giữa các tác tử.
- H2 (skills-auto so với baseline): Dự đoán skills-auto sẽ đạt điểm cao hơn rõ rệt so với baseline trên các tác vụ đánh giá (đặc biệt là các check quy ước ngầm nhóm E như cấu trúc meta block, định dạng output, quy ước Acme), vì curator đã chắt lọc các quy ước này thành các skill có thể tái sử dụng trong thư mục skills/auto và tác tử đã đọc 3/3 skill.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trung bình trên tác vụ học (learn) sẽ cao hơn tác vụ đánh giá (eval) ở điều kiện skills-auto do một phần quy tắc trong skill có thể bị quá khớp (overfitting) với đặc thù của các bài tập trong tập học, tuy nhiên các quy tắc tổng quát (như kiểm tra lỗi, tuân thủ định dạng output) vẫn giúp ích cho tập đánh giá so với baseline.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Trong đó, công cụ cho phép chạy lệnh shell là `execute`.
2. Mô tả của công cụ `task` về subagent `general-purpose`: "General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks... This agent has access to all tools as the main agent." Subagent này hoạt động ở chế độ stateless ("the agent sees only the prompt you give it and returns a single final report"), không tự động thừa hưởng toàn bộ lịch sử hội thoại trước đó của tác tử chính mà chỉ thấy prompt được giao.
3. Trích dẫn hướng dẫn hành vi:
   - Từ mô tả công cụ `task`: *"Put full detail in the prompt and state exactly what it should return unless an agent type below says it inherits your conversation instead."*
   - Từ mô tả công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | rule_test_file | E | `RULE: add a regression test file workspace/tests/test_pricing_fixes.py with at least two test functions reproducing and verifying fixes.` |
| code-learn | rule_changelog | E | `RULE: append an entry to workspace/CHANGELOG.md under ## Unreleased describing the bug fixes.` |
| code-learn | rule_type_annotations | E | `RULE: every public function in inventory/ must have complete Python type annotations on all parameters and return value.` |
| code-learn | rule_public_exports | E | `RULE: inventory/__init__.py must define __all__ re-exporting parse_price, apply_discount, to_csv_row, total_value, low_stock.` |
| data-learn | rule_money_in_cents | E | `RULE: in workspace/answer.json all monetary values must be represented as integer cents (e.g. 1000 for $10.00).` |
| data-learn | rule_meta_block | E | `RULE: in workspace/answer.json include a top-level "meta" object containing "source_file", "generated_at" (ISO-8601 UTC), and "version" ("1.0").` |
| data-learn | rule_clean_csv | E | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount.` |
| logs-learn | rule_schema_version | E | `RULE: in workspace/report.json include a top-level key "schema_version": "2.1".` |
| logs-learn | rule_sha256 | E | `RULE: in workspace/report.json include a top-level key "input_sha256" with the hex-encoded SHA-256 of workspace/app.log.` |
| logs-learn | rule_log_summary | E | `RULE: create workspace/log_summary.txt containing a human-readable text summary of the error counts per component.` |

Nhận xét:
- Nhóm lỗi **E (Vi phạm quy ước tổ chức)** chiếm tuyệt đối 100% trong số các check thất bại được phân loại (9/9 check `rule_`). Nguyên nhân chung là do đề bài tác vụ cố tình không mô tả chi tiết các "Acme house rules" này mà để ẩn trong bộ chấm điểm (`grading.py`).
- Các check kỹ thuật (A-D) đạt 12/18 ở baseline và tăng lên 17/18 ở subagents/skills-auto (làm bằng chứng phủ định cho việc mô hình không bị hổng năng lực logic cốt lõi).
- Một skill tự động tổng hợp (Curator) có thể phòng ngừa hoàn toàn nhóm lỗi E bằng cách phát hiện các phản hồi `detail` thất bại và biên soạn thành các hướng dẫn bắt buộc (checklist) trước khi hoàn tất tác vụ.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  - `explorer`: Đọc tài liệu, cấu trúc thư mục, code hiện có mà không sửa đổi file; hỗ trợ khảo sát ban đầu.
  - `implementer`: Trực tiếp viết code, chạy script, sửa lỗi và thực thi kiểm thử.
  - `reviewer`: Kiểm tra độc lập nghiệm thu so với các yêu cầu và quy tắc trước khi hoàn tất.
- `subagent_calls` ở từng tác vụ:
  - `code-learn`: 1 cuộc gọi (tác tử chính giao việc cho subagent giải quyết và review, điểm số tăng từ 6/10 lên 7/10).
  - `data-learn`: 0 cuộc gọi (tác tử chính tự chạy script Python xử lý dữ liệu và tính toán).
  - `logs-learn`: 0 cuộc gọi (tác tử chính tự phân tích log file và xuất JSON).
- Nhận xét việc giao việc: Khi giao việc ở `code-learn`, tác tử chính truyền đầy đủ mô tả tác vụ và các quy ước đường dẫn (`workspace/...`), subagent thực hiện xong gửi báo cáo chi tiết và tác tử chính đã kiểm chứng lại kết quả.
- Ảnh hưởng đến token và thời gian: Trung bình token tăng nhẹ (~452,067 so với ~442,341 ở baseline), thời gian thực thi tương đương (~50s/task).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 1 lần. Số skill bị xóa: 0 (tất cả 3 skill sinh ra đều hợp lệ và vượt qua bài kiểm tra `test_04_curator.py`).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `output-verification` | Tổng quát | Đúng (hướng dẫn xác minh đầy đủ file output, vị trí, format trước khi kết thúc) | 11 dòng; description rõ ràng; `skills_read = 3` |
| `project-convention-compliance` | Tổng quát | Đúng (hướng dẫn kiểm tra type annotations, file phụ trợ, format rules) | 12 dòng; description rõ ràng; `skills_read = 3` |
| `thorough-code-reading` | Tổng quát | Đúng (hướng dẫn đọc kỹ docstring, edge-case, không phỏng đoán theo tên hàm) | 11 dòng; description rõ ràng; `skills_read = 3` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

```text
(sẽ cập nhật bảng kết quả chính thức sau khi chạy tập eval)
```

## 8. Phân tích

(sẽ hoàn thiện sau khi chạy xong tập eval)

## 9. Hạn chế và tính hợp lệ

1. **Số lượng tác vụ hạn chế**: Mỗi vai trò chỉ có 3 tác vụ học và 3 tác vụ đánh giá (tổng cộng 6 tác vụ). Kích thước mẫu nhỏ khiến các chỉ số thống kê dễ bị ảnh hưởng bởi từng bài toán cụ thể.
2. **Đo lường đơn lượt (single run)**: Mỗi cấu hình chỉ chạy 1 lần do giới hạn tài nguyên và thời gian, không lấy trung bình qua nhiều seed/lần chạy nên có thể chịu ảnh hưởng từ độ ngẫu nhiên của mô hình.
3. **Quy ước thiết kế nhân tạo**: Các check `rule_` được nhóm tác giả lab cố tình đặt ra để đo lường khả năng học quy ước ẩn của Curator, có thể không phản ánh đầy đủ tính đa dạng của quy ước dự án trong các kho mã nguồn thực tế.

## 10. Kết luận

(sẽ cập nhật sau khi chạy xong tập eval)

## Phụ lục

- Lệnh đã chạy:
  1. `pytest`
  2. `python -m lab.runner --condition baseline --tasks learn --recursion-limit 120`
  3. `python -m lab.runner --condition subagents --tasks learn --recursion-limit 120`
  4. `python -m lab.curator`
  5. `python -m lab.runner --condition skills-auto --tasks learn --recursion-limit 120`
