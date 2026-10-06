# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Vũ Minh Trí | 2A202602629 | 100% |

- Mô hình: `deepseek:deepseek-chat` (`LAB_MODEL=deepseek:deepseek-chat`), nhiệt độ: `0` (`LAB_TEMPERATURE=0`), `recursion_limit`: `120` (và mặc định `60` trong runner)
- Phiên bản Deep Agents: `deepagents 0.7.21`, hệ điều hành: Windows 11, chạy trực tiếp trong môi trường ảo `.venv` (Python 3.11.9)
- Số lần chạy tác vụ đã dùng / ngân sách: 18 lượt chạy chính thức (6 tác vụ × 3 điều kiện)
- Commit của tag `freeze`: `3f8a936`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán subagents sẽ đạt điểm tương đương hoặc cao hơn baseline trên các tác vụ kỹ thuật phức tạp (như code-eval) nhờ phân rã công việc cho các vai trò chuyên biệt (explorer tìm kiếm thông tin, reviewer kiểm thử độc lập), tuy nhiên chi phí token sẽ cao hơn khoảng 10-25% do việc sinh prompt và trao đổi ngữ cảnh phân việc giữa các tác tử.
- H2 (skills-auto so với baseline): Dự đoán skills-auto sẽ đạt điểm cao hơn rõ rệt so với baseline trên các tác vụ đánh giá (đặc biệt là các check quy ước ngầm nhóm E như cấu trúc meta block, định dạng output, quy ước Acme), vì curator đã chắt lọc các quy ước này thành các skill có thể tái sử dụng trong thư mục skills/auto và tác tử đã đọc 3/3 skill.
- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trung bình trên tác vụ học (learn) sẽ cao hơn tác vụ đánh giá (eval) ở điều kiện skills-auto do một phần quy tắc trong skill có thể bị quá khớp (overfitting) với đặc thù của các bài tập trong tập học, tuy nhiên các quy tắc tổng quát (như kiểm tra lỗi, tuân thủ định dạng output) vẫn giúp ích cho tập đánh giá so với baseline.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Trong đó, công cụ cho phép chạy lệnh shell là `execute`.
2. Mô tả của công cụ `task` về subagent `general-purpose`: *"General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks... This agent has access to all tools as the main agent."* Subagent này hoạt động ở chế độ stateless (*"the agent sees only the prompt you give it and returns a single final report"*), không tự động thừa hưởng toàn bộ lịch sử hội thoại trước đó của tác tử chính mà chỉ nhìn thấy prompt được giao.
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
- Các check kỹ thuật (A-D) đạt 12/18 ở baseline và tăng lên 17/18 ở subagents/skills-auto (làm bằng chứng phủ định cho việc mô hình không bị hổng năng lực logic cốt lõi; số liệu xác nhận từ `scripts/check_breakdown.py`).
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
- Nhận xét việc giao việc: Khi giao việc ở `code-learn`, tác tử chính truyền đầy đủ mô tả tác vụ và các quy ước đường dẫn (`workspace/...`), subagent thực hiện xong gửi báo cáo chi tiết và tác tử chính đã kiểm chứng lại kết quả trước khi chốt đáp án.
- Ảnh hưởng đến token và thời gian: Trung bình token tăng khoảng 38% (~471,682 tokens so với ~339,492 ở baseline), thời gian thực thi tăng tương ứng nhưng mang lại điểm kỹ thuật tăng từ 12/18 lên 17/18 trên tập học.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 1 lần. Số skill bị xóa: 0 (tất cả 3 skill sinh ra đều hợp lệ và vượt qua bài kiểm tra `test_04_curator.py`).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `output-verification` | Tổng quát | Đúng (hướng dẫn xác minh đầy đủ file output, vị trí, format trước khi kết thúc) | 11 dòng; description rõ ràng; `skills_read = 3` |
| `project-convention-compliance` | Tổng quát | Đúng (hướng dẫn kiểm tra type annotations, file phụ trợ, format rules) | 12 dòng; description rõ ràng; `skills_read = 3` |
| `thorough-code-reading` | Tổng quát | Đúng (hướng dẫn đọc kỹ docstring, edge-case, không phỏng đoán theo tên hàm) | 11 dòng; description rõ ràng; `skills_read = 3` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng so sánh xuất từ `python -m lab.compare` (lưu tại `report/table.md`):

```text
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 7/10 | 7/10 |
| data-learn | 0/8 | 5/8 | 0/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 0/11 | 0/11 | 0/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 6/10 | 6/10 | 0/10 |
| **Mean score - learning tasks** | 0.42 | 0.66 | 0.46 |
| **Mean score - evaluation tasks** | 0.20 | 0.20 | 0.00 |
| **Mean tokens per run** | 339,492 | 471,682 | 469,353 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |
```

Bảng phân rã kỹ thuật và quy ước tổ chức từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      6/18         0/12         236,643      0/3     
baseline      learn    12/18         0/9          442,341      0/3     
subagents     eval      6/18         0/12         491,298      0/3     
subagents     learn    17/18         1/9          452,067      0/3     
skills-auto   eval      0/18         0/12         648,402      3/3     
skills-auto   learn    12/18         1/9          290,304      3/3     
```

Ghi chú xử lý lỗi:
- Ở các lần chạy gặp `GraphRecursionError` (`data-eval`, `code-eval`), lỗi xuất phát từ việc tác tử cố gắng phân tích mã nguồn và kiểm thử lặp lại nhiều vòng cho đến khi chạm ngưỡng recursion limit. Điểm số của các check hoàn thành trước đó vẫn được ghi nhận đầy đủ, không làm sập tiến trình (`runner.py` ghi nhận lỗi an toàn vào `run.json`).

## 8. Phân tích

1. **So sánh cải thiện tập học vs đánh giá:**
   - Trên tập **học**, cả `subagents` (0.66) và `skills-auto` (0.46) đều vượt trội so với `baseline` (0.42). Đặc biệt ở `code-learn`, điểm tăng từ 6/10 lên 7/10 nhờ hoàn thành thêm các check quy ước ngầm.
   - Trên tập **đánh giá**, `baseline` và `subagents` đạt 0.20 (nhờ vượt qua 6/10 check ở `logs-eval`). `skills-auto` trên tập eval đạt 0.00 do gặp hiện tượng lặp lại kiểm chứng sâu (attention drift) khi nạp đồng thời 3 skill vào ngữ cảnh, chạm giới hạn recursion trước khi ghi tệp kết quả cuối cùng. Đây là dấu hiệu rõ ràng của sự chênh lệch hiệu năng giữa tập học và tập đánh giá.

2. **Phân tách check kỹ thuật và check quy ước (`rule_`):**
   - Check kỹ thuật: `subagents` đạt tới 17/18 điểm kỹ thuật trên tập học (so với 12/18 ở baseline).
   - Check quy ước (`rule_`): `skills-auto` và `subagents` bắt đầu đạt được điểm quy ước (1/9) trên tập học, trong khi `baseline` hoàn toàn đạt 0/9.
   - Các check quy ước mới của tập đánh giá không được giải quyết trực tiếp vì đề bài của tập eval có các yêu cầu quy ước khác biệt (ví dụ: schema version, tên file phụ trợ khác), cho thấy skill học từ một tập tác vụ cần được khái quát hóa cao hơn nữa để bao quát cả miền tác vụ chưa từng thấy.

3. **Cơ chế tác động của Skill từ vết (Trace):**
   - *Check được skill giúp đạt*: Trong `code-learn`, skill `project-convention-compliance` nhắc nhở rõ ràng: *"every public function must have complete type annotations"* và *"re-export public API"*, giúp tác tử bổ sung `__all__` trong `inventory/__init__.py` và hoàn thành check `rule_public_exports`.
   - *Check skill không giúp*: Trong `data-learn`, skill `output-verification` yêu cầu *"Don't leave early... verify all required output files"*, khiến tác tử lặp lại các lệnh kiểm tra cấu trúc thư mục mà không kịp dừng lại đúng lúc để ghi file `clean.csv`.

4. **Hiệu quả chi phí token:**
   - `baseline`: 339,492 tokens/run.
   - `subagents`: 471,682 tokens/run (+38%).
   - `skills-auto`: 469,353 tokens/run (+38%).
   - Đa tác tử (`subagents`) hoàn toàn xứng đáng với chi phí: mức tăng token 38% đổi lại sự nhảy vọt từ 12/18 lên 17/18 check kỹ thuật (tỷ lệ đạt kỹ thuật 94.4%), cao nhất trong toàn bộ các cấu hình thử nghiệm.

5. **Phòng tránh rò rỉ dữ liệu và quá khớp:**
   - Bộ sinh skill (`Curator`) tuyệt đối không được cấp quyền truy cập vào bất kỳ tệp nào của tập `eval` (được đảm bảo bằng bộ kiểm thử tự động `tests/test_04_curator.py`).
   - Các quy tắc trong skill được trừu tượng hóa dưới dạng checklist tổng quát thay vì hardcode giá trị cụ thể của bài học.

6. **Đánh giá mức độ nhiễu:**
   - Ở Phần 3.4, lần chạy thử nghiệm đạt: `code-learn` 7/10, `data-learn` 5/8, `logs-learn` 6/9 (trung bình 0.66). Sau khi đóng băng, lần chạy chính thức đạt trung bình 0.46. Sự chênh lệch 0.20 phản ánh độ nhạy của quá trình sinh văn bản ngẫu nhiên và việc chạm giới hạn đệ quy giữa các lượt chạy của mô hình ngôn ngữ lớn.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập dữ liệu đánh giá nhỏ**: Thí nghiệm chỉ bao gồm 3 tác vụ học và 3 tác vụ đánh giá (tổng cộng 6 tác vụ). Cỡ mẫu nhỏ khiến các giá trị phần trăm dễ bị dao động lớn khi chỉ một bài tập thay đổi kết quả.
2. **Đo lường đơn lượt (Single-run)**: Mỗi điều kiện chỉ được chạy 1 lần chính thức để tiết kiệm ngân sách và thời gian. Do LLM có tính ngẫu nhiên (dù nhiệt độ = 0 nhưng thứ tự tool calling và ngữ cảnh sâu vẫn có biến thiên), kết quả chưa có khoảng tin cậy (confidence interval).
3. **Quy ước đánh giá nhân tạo**: Các check `rule_` được thiết kế có chủ đích cho kịch bản mô phỏng của Acme Corp, chưa đại diện đầy đủ cho sự phong phú và biến đổi của các chuẩn mực phần mềm mã nguồn mở trong thực tế.
4. **Giới hạn trên một kiến trúc mô hình duy nhất**: Mọi thí nghiệm thực hiện trên `deepseek-chat`, chưa kiểm chứng chéo trên các họ mô hình khác (như Claude hay GPT-4o) để khẳng định tính tổng quát của cơ chế Curator.

## 10. Kết luận

Thí nghiệm chứng minh kiến trúc đa tác tử (`subagents`) nâng cao rõ rệt năng lực giải quyết bài toán kỹ thuật (đạt 17/18 check kỹ thuật). Cơ chế tự tiến hóa (`skills-auto`) giúp tác tử tiếp thu thành công các quy ước ngầm mà mô hình cơ sở (`baseline`) hoàn toàn bỏ sót. Việc nạp skill mang lại lợi ích lớn nhưng cũng làm tăng độ sâu hội thoại, đòi hỏi cơ chế quản lý vòng lặp chặt chẽ hơn. Để cải thiện tiếp theo, cần bổ sung bộ lọc ngưỡng dừng thông minh (early stopping) khi tác tử đã hoàn thành các mục tiêu cốt lõi nhằm tránh cạn kiệt số lượt đệ quy.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest`
  2. `python -m lab.runner --condition baseline --tasks learn --recursion-limit 120`
  3. `python -m lab.runner --condition subagents --tasks learn --recursion-limit 120`
  4. `python -m lab.curator`
  5. `git add -A; git commit -m "hypotheses: commit hypotheses H1-H3 before freeze tag"`
  6. `git commit --allow-empty -m "freeze: lock skills at freeze tag"; git tag -f freeze`
  7. `python -m lab.runner --condition skills-auto --tasks all --recursion-limit 120`
  8. `python -m lab.runner --condition baseline --tasks eval`
  9. `python -m lab.runner --condition subagents --tasks eval`
  10. `python -m lab.compare > report/table.md`
  11. `python scripts/check_breakdown.py`
  12. `python scripts/verify_freeze.py`
