# Lab: Bộ khung điều khiển tác tử (Agent Harness), tác tử tự tiến hóa (Self-Evolving Agent) và đa tác tử (Multi-Agent) với Deep Agents

Thời lượng: 4 giờ trên lớp, cộng khoảng 45 phút hoàn thiện báo cáo sau lớp. Hình thức: thực hành cá nhân hoặc nhóm 2 đến 3 sinh viên. Ngôn ngữ lập trình: Python 3.11 trở lên.

## 1. Mục tiêu học tập

Sau lab, sinh viên có khả năng:

1. Dựng một tác tử bằng thư viện Deep Agents (LangChain) và mô tả các thành phần của bộ khung điều khiển (harness): công cụ (tool), môi trường thực thi (backend), system prompt, tác tử con (subagent), kỹ năng (skill).
2. Xây dựng quy trình chạy thí nghiệm có thể lặp lại: cô lập môi trường (sandbox), đo token, thời gian, số lần gọi công cụ, chấm điểm tự động.
3. Cải thiện tác tử ở tầng ngữ cảnh (context layer) bằng skill: viết tay và sinh tự động từ phản hồi và vết thực thi (trace).
4. Đánh giá đúng cách một cải tiến: tách tập học (learning set) và tập đánh giá (evaluation set), đóng băng (freeze) skill trước khi đánh giá, nhận diện quá khớp (overfitting) và rò rỉ dữ liệu (data leakage).
5. So sánh chi phí và hiệu quả của đa tác tử (subagent) với một tác tử.

## 2. Thiết kế thí nghiệm

### 2.1. Tác vụ (task) và quy ước tổ chức (house rules)

Có 3 họ tác vụ (family). Mỗi họ có 1 tác vụ học và 1 tác vụ đánh giá, tổng 6 tác vụ. Mỗi tác vụ được chấm bằng các phép kiểm tra tự động (check) gồm hai loại:

| Loại check | Nội dung | Ví dụ |
|---|---|---|
| Kỹ thuật | Làm đúng việc: sửa đúng lỗi, làm sạch đúng dữ liệu, phân tích đúng log | Đổi múi giờ về UTC, loại dòng trùng, gộp dòng lặp của log |
| Quy ước tổ chức (house rules) | Quy tắc của tổ chức "Acme" **không được nêu trong đề**; đề chỉ nói rằng bot đánh giá của Acme sẽ kiểm tra thêm. Tên các check này bắt đầu bằng `rule_` | Đơn vị tiền tệ, khối `meta`, tệp `clean.csv`, thứ tự sắp xếp, tiêu đề lược đồ |

Cách hoạt động của phản hồi (feedback):

- Ở **tác vụ học**, check thất bại có trường `detail` trong `run.json`: nội dung là nhận xét của bot đánh giá, phát biểu quy tắc bị vi phạm. `detail` **không chứa đáp án**. Đây là nguồn để rút ra skill.
- Ở **tác vụ đánh giá**, `detail` luôn rỗng. Tác vụ đánh giá dùng lại các quy tắc của tác vụ học và thêm **một quy tắc mới** không thể suy ra từ tác vụ học. Vì vậy một skill tốt giúp được phần lớn check quy ước, nhưng không giúp được quy tắc mới.

| Họ | Tác vụ học | Tác vụ đánh giá | Nội dung kỹ thuật |
|---|---|---|---|
| `code` | `code-learn` | `code-eval` | Sửa lỗi gói Python nhỏ: lỗi gốc nằm ở hàm dùng chung, và có lỗi chỉ thấy khi đối chiếu docstring (test hiển thị không phủ hết). |
| `data` | `data-learn` | `data-eval` | Trả lời câu hỏi có đáp án chính xác từ tệp CSV/JSON bẩn: dòng trùng, giá trị thiếu, nhiều định dạng ngày, múi giờ. |
| `logs` | `logs-learn` | `logs-eval` | Phân tích tệp log thành JSON: stack trace nhiều dòng, dòng lặp, nhiều cách viết mức log, múi giờ. |

Điểm của tác vụ là tỉ lệ check đạt (chấm từng phần - partial credit).

### 2.2. Bốn điều kiện thí nghiệm (condition)

| Điều kiện | Mô tả |
|---|---|
| `baseline` | Tác tử Deep Agents mặc định, không có skill. Đường cơ sở để so sánh. |
| `subagents` | Thêm các subagent do nhóm định nghĩa (đa tác tử). |
| `skills-human` | Nạp skill do nhóm viết tay từ phản hồi của tác vụ học. |
| `skills-auto` | Nạp skill do bộ tuyển chọn skill (curator) tự sinh từ phản hồi và vết của tác vụ học. |

### 2.3. Quy trình đóng băng (freeze) và quy tắc xem dữ liệu

1. Chỉ được mở `run.json` và `trace.md` của **tác vụ học** để rút kinh nghiệm. Không mở `run.json`, `trace.md` của tác vụ đánh giá và thư mục `tasks/*-eval/`.
2. Không mở tệp `check.py` của bất kỳ tác vụ nào (chứa đáp án kỳ vọng). Phản hồi hợp lệ nằm trong `run.json`, chỉ ở các check **thất bại** của tác vụ học.
3. Tên do **quy ước của Acme** yêu cầu (tệp đầu ra như `clean.csv`, `tests/test_regressions.py`, khóa JSON như `meta`, tiêu đề) được phép xuất hiện trong skill vì chúng chính là quy tắc. Tên **có sẵn trong workspace của tác vụ** (tệp dữ liệu, hàm, cột) và mọi định danh của tác vụ đánh giá thì không.
4. Ở giai đoạn đầu chỉ chạy `baseline` và `subagents` trên tác vụ học (`--tasks learn`), nên giả thuyết của nhóm được viết trước khi thấy bất kỳ điểm nào của tác vụ đánh giá.
5. Sau khi viết giả thuyết, chốt skill và tạo tag git `freeze`. Từ thời điểm này không được sửa skill.
6. Chạy các điều kiện trên tác vụ đánh giá, rồi kiểm tra bằng `python scripts/verify_freeze.py`.

Quy trình này mô phỏng cách các nghiên cứu về tiến hóa skill (SkillsBench, SkillEvolBench) tách giai đoạn học và giai đoạn triển khai.

## 3. Cấu trúc thư mục

```text
<tên-kho>/
├── README.md              Tài liệu này
├── GUIDE.md               Hướng dẫn thực hiện từng bước theo thời gian
├── RUBRIC.md              Thang điểm 100
├── GLOSSARY.md            Bảng thuật ngữ
├── REPORT_TEMPLATE.md     Mẫu báo cáo
├── pyproject.toml         Khai báo thư viện
├── .env.example           Mẫu cấu hình khóa API
├── Dockerfile             (tùy chọn) chạy trong container
├── guides/pseudocode/     Pseudo-code cho từng module sinh viên phải cài đặt
├── src/lab/               Mã nguồn
│   ├── model.py, tasks.py, grading.py, testing.py, compare.py   Có sẵn, không sửa
│   └── agent.py, subagents.py, runner.py, curator.py             SINH VIÊN CÀI ĐẶT (mỗi tệp còn lại vài hàm TODO)
├── tasks/                 6 tác vụ (workspace, instruction.md, check.py)
├── tests/                 Bộ test ngoại tuyến (offline), không tốn token
├── scripts/               tour.py (xem công cụ mặc định), verify_freeze.py (kiểm tra đóng băng), check_breakdown.py (thống kê check)
├── skills/human/          Skill viết tay (sinh viên tạo)
├── skills/auto/           Skill tự sinh (curator ghi)
├── report/                Báo cáo của sinh viên (bạn tạo ở Phần 0: REPORT.md, table.md)
└── results/               Kết quả các lần chạy (chương trình ghi)
```

## 4. Cài đặt

Yêu cầu: Python 3.11 trở lên; hệ điều hành macOS hoặc Linux (trên Windows dùng WSL hoặc Docker, vì shell của tác tử dùng `/bin/sh`); thông tin truy cập mô hình do giảng viên cấp.

```bash
git clone <URL-kho-mã-nguồn> && cd <tên-kho>
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
mkdir -p report && cp REPORT_TEMPLATE.md report/REPORT.md
pytest tests/test_01_provided.py
```

Điền `.env` theo một trong hai cách (`model.py` ưu tiên cách 1 nếu cả ba biến của cách 1 đều có):

1. **Azure OpenAI hoặc cổng tương thích OpenAI**: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT_MODEL`.
2. **Nhà cung cấp khác** (ví dụ DeepSeek): `LAB_MODEL=deepseek:deepseek-chat` và `DEEPSEEK_API_KEY`. Tên mô hình thay đổi theo thời gian, đối chiếu tài liệu của nhà cung cấp.

Kết quả mong đợi của `pytest tests/test_01_provided.py`: `12 passed`. Không commit tệp `.env`.

## 5. Lịch thực hiện

| Thời gian | Phần | Nội dung | Sản phẩm |
|---|---|---|---|
| 0:00 - 0:20 | 0 | Cài đặt, xem công cụ của tác tử mặc định (`scripts/tour.py`) | `test_01` đạt |
| 0:20 - 1:00 | 1 | Cài đặt `subagents.py`, `agent.py` (`make_backend`, `build_agent`), `runner.py` (`run_task`) | `test_02`, `test_03` đạt |
| 1:00 - 1:35 | 2 | Chạy `baseline` và `subagents` trên tác vụ học; phân loại lỗi | Bảng phân loại lỗi |
| 1:35 - 1:45 | | Nghỉ | |
| 1:45 - 2:25 | 3 | Viết skill bằng tay từ phản hồi của tác vụ học | `skills/human/` |
| 2:25 - 2:55 | 4 | Cài đặt `curate_skills`, chạy curator, đánh giá skill tự sinh | `skills/auto/`, `test_04` đạt |
| 2:55 - 3:25 | 5 | Giả thuyết, đóng băng, chạy tác vụ đánh giá, tạo bảng so sánh | `results/`, `report/table.md` |
| 3:25 - 3:50 | 6 | Viết bản nháp báo cáo (mục 1 đến 8) | `report/REPORT.md` (nháp) |
| 3:50 - 4:00 | | Tổng kết | |
| Sau lớp, tối đa 45 phút | 6 | Hoàn thiện mục 9 đến 11 của báo cáo và nộp bài | Báo cáo hoàn chỉnh |

Sinh viên chậm có thể cần thêm thời gian ở Phần 1 và Phần 3; phần đã có sẵn (`render_trace`, `main` của runner, `validate_skill`, `parse_skill_blocks`, `compare.py`, `check_breakdown.py`) được cung cấp để giữ lab trong khuôn khổ 4 giờ.

Phần 7 (thử thách mở rộng) là tùy chọn, tối đa +5 điểm.

## 6. Sản phẩm nộp

Nộp qua kho mã nguồn (git), gồm:

1. Mã nguồn đã cài đặt trong `src/lab/` (4 tệp: `agent.py`, `subagents.py`, `runner.py`, `curator.py`; chỉ các hàm đánh dấu TODO).
2. `skills/human/` và `skills/auto/`.
3. `results/` (đủ `run.json` và `trace.md` của các lần chạy dùng trong báo cáo).
4. `report/REPORT.md` và `report/table.md`.
5. Tag git `freeze` trên commit chốt skill; `python scripts/verify_freeze.py` báo OK.

Thang điểm chi tiết: xem `RUBRIC.md`.

## 7. Quy tắc

**Liêm chính học thuật.** Tuân thủ mục 2.3. Không chép đáp án vào skill. Skill chứa tên tệp hay định danh của tác vụ đánh giá bị curator từ chối và bị trừ điểm nếu viết tay.

**An toàn.** Tác tử chạy lệnh shell thật trên máy. Môi trường cách ly (sandbox) trong lab là thư mục tạm, chưa phải cách ly ở mức hệ điều hành. Khuyến nghị chạy trong Docker (`Dockerfile`). Không đưa khóa API vào mã nguồn, vào `trace.md` hay báo cáo. `trace.md` đã được thay đường dẫn thư mục người dùng bằng `~`; vẫn nên đọc lại trước khi nộp.

**Ngân sách token.** Tối đa 48 lần chạy tác vụ cho mỗi nhóm. Gợi ý phân bổ: `baseline` 6, `subagents` 6, phát triển skill 6 đến 9 (chỉ tác vụ học), chạy cuối sau đóng băng 12, dự phòng cho lỗi và chạy lại 15. Mỗi lần chạy thường dùng khoảng 15 nghìn đến 150 nghìn token tùy tác vụ và điều kiện. Giữ `--recursion-limit` mặc định hoặc thấp hơn. Dùng `pytest` và `ScriptedChatModel` để kiểm tra mã trước khi chạy mô hình thật. Giảng viên có thể điều chỉnh ngân sách theo hạn mức của lớp.

**Sao lưu kết quả.** Chạy lại cùng một điều kiện sẽ ghi đè `results/<điều kiện>/`. Nếu cần giữ bằng chứng cũ, đổi tên thư mục trước khi chạy lại (ví dụ `mv results/baseline results/baseline-v1`). `lab.compare` chỉ đọc bốn thư mục điều kiện đúng tên (`baseline`, `subagents`, `skills-human`, `skills-auto`) nên thư mục có hậu tố không lẫn vào bảng.

## 8. Tài liệu tham khảo

- Deep Agents: <https://docs.langchain.com/oss/python/deepagents> (subagents: <https://docs.langchain.com/oss/python/deepagents/subagents>).
- Agent Skills (chuẩn định dạng skill): <https://agentskills.io/>.
- Anthropic, *How we built our multi-agent research system*: <https://www.anthropic.com/engineering/multi-agent-research-system>.
- Xia et al., *Live-SWE-agent*: <https://arxiv.org/abs/2511.13646>.
- Zhang et al., *Darwin Gödel Machine*: <https://arxiv.org/abs/2505.22954>.
- Shinn et al., *Reflexion*: <https://arxiv.org/abs/2303.11366>.
- Wang et al., *Voyager*: <https://arxiv.org/abs/2305.16291>.
- *Agentic Context Engineering (ACE)*: <https://arxiv.org/abs/2510.04618>.
- *A Survey of Self-Evolving Agents*: <https://arxiv.org/html/2507.21046v4>.
- SkillsBench: <https://www.emergentmind.com/papers/2602.12670>; SkillEvolBench: <https://arxiv.org/html/2605.24117v1>.
