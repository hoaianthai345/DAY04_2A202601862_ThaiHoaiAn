# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Day 04 — Research Agent Tool Eval
- Thái Hoài An — 2A202601862 — TV1: setup, tool mới, baseline và 5 single-turn eval
- Nguyễn Minh Hiếu — 2A202601154 — TV2: tối ưu v1–v3, version log và group eval cuối
- Dương Ngọc Hải — 2A202601748 — TV3: UI, 5 multi-turn eval, demo và report
- Provider baseline: OpenRouter / `openai/gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent thu thập thông tin qua web, mạng xã hội hoặc URL có sẵn; sau đó có thể kiểm tra provenance của nguồn và định dạng kết quả thành digest. Agent lưu tool trace, run JSON và transcript để nhóm đánh giá routing/arguments bằng evidence thay vì chỉ nhìn câu trả lời cuối.

**Link dùng thử:** `http://localhost:8501` khi chạy Streamlit trên máy demo. Public tunnel: pending TV3.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu URL, handle hoặc cần xác nhận. | Không |
| `timeline` | Lấy bài đăng mới từ một tài khoản theo handle. | Không |
| `social_search` | Tìm bài đăng theo chủ đề, `Latest` hoặc `Top`. | Không |
| `lookup` | Tìm web/tin tức theo query, topic và timeframe. | Không |
| `fetch` | Đọc nội dung một URL cụ thể. | Không |
| `source_check` | Phân loại provenance của URL: official, research archive, news publisher hoặc unclassified. | **Có** |
| `format` | Định dạng item có sẵn thành markdown digest. | Không |
| `send` | Gửi Telegram sau confirmation; optional, không dùng để claim tool mới. | Không |

## A3. Câu hỏi mẫu để thử

1. `Tin AI hôm nay có gì nổi bật?`
2. `Lấy 5 tweet mới nhất của Elon Musk.`
3. `Tóm tắt bài này: https://openai.com/index/introducing-gpt-5`
4. `Link https://arxiv.org/abs/1706.03762 thuộc loại nguồn nào trước khi trích dẫn?`
5. `Đăng bản tin này lên Telegram giúp mình.` — Agent phải hỏi xác nhận trước.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện version | Fallback run/transcript |
|---|---|---|---|
| Tin AI hôm nay | `lookup(query="AI", topic="news", timeframe="day")` | v0 đã đo được routing news; TV2 sẽ chuẩn hoá query không thêm từ `news`. | `runs/v0_B_base_openrouter_20260729T152819647169.json` — R03 |
| Thiếu handle | `clarify(response_type="text")` | v0 gọi nhầm `timeline(sama)`; v1 cần hỏi lại thay vì đoán. | v0 — R10 |
| Thiếu URL | `clarify(response_type="text")` | v0 tự dùng URL mẫu; v1 cần chặn suy đoán URL. | v0 — R11 |
| Gửi Telegram | `clarify(response_type="yes_no")`, chỉ sau đó mới `send` | v0 gọi `send` ngay; v1 cần siết confirmation boundary. | v0 — R12 |
| Kiểm tra nguồn | `source_check(url=...)` | Tool mới phân biệt nguồn official/research trước khi trích dẫn. | `data/eval_group.json` — G01–G04 |

---

# PHẦN B — Chi tiết / Bằng chứng

> Metric hợp lệ khi `provider_error_cases = 0` và `measured_cases = total_cases`. Run v0 dưới đây đạt hai điều kiện này. Các run Groq bị rate limit chỉ dùng để chẩn đoán, không dùng làm metric report.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline, chưa tối ưu prompt/declaration. | Đo routing và boundary ban đầu. | Case accuracy | — | 0.65 | `runs/v0_B_base_openrouter_20260729T152819647169.json` |
| v1 | Sửa `system_prompt.md`: scope, clarify, confirmation, handle mapping. | Quy tắc rõ hơn giảm đoán handle/URL và gọi action sớm. | Case accuracy | 0.65 | 0.65 | `runs/v1_B_base_openrouter_20260729T160039032723.json` |
| v2 | Sửa `tools.yaml`: usage boundaries và argument conventions. | Description rõ giúp phân biệt routing giữa tools. | Case accuracy | 0.65 | 0.90 | `runs/v2_B_base_openrouter_20260729T160758249744.json` |
| v3 | Sửa prompt: short query, response type và parallel calls. | Xử lý các lỗi arguments/boundary còn lại. | Case accuracy | 0.90 | 0.90 | `runs/v3_B_base_openrouter_20260729T160929985283.json` |

Các run OpenRouter v0–v3 được dùng trong bảng đều có 20/20 measured cases và 0 provider errors. Snapshot prompt/tools tương ứng nằm trong `artifacts/versions/v0` đến `artifacts/versions/v3`; root `artifacts/` giữ bản active v3.

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix đề xuất cho TV2 |
|---|---|---|---|---|
| R03 | `wrong_tool` | `lookup(query="AI news", topic="news", timeframe="day")` | Query phải là `AI`, model thêm `news`. | Quy ước query chỉ giữ chủ đề; news là field `topic`. |
| R08 | `out_of_scope` | `send(text=...)` | Câu hỏi tích phân phải không gọi tool nhưng model dùng `send`. | Chặn out-of-scope và cô lập optional `send`. |
| R10 | `missing_info` | `timeline(screenname="sama")` | Thiếu handle nhưng model tự đoán Sam Altman. | Bắt buộc `clarify` khi không có handle. |
| R11 | `missing_info` | `fetch(url="https://example.com/article")` | Thiếu URL nhưng model tự tạo URL mẫu. | Bắt buộc `clarify` khi không có URL. |
| R12 | `wrong_boundary` | `send(text=...)` | Gửi Telegram ngay, không hỏi yes/no. | Confirmation boundary trước mọi action. |
| R13 | `wrong_tool` | `lookup(query="AI news", timeframe="day")` + `social_search(...)` | Sai query `AI news` và thiếu `topic="news"`. | Nêu rõ conventions cho parallel web + social routing. |
| R14 | `out_of_scope` | `send(text=...)` | Câu coding ngoài phạm vi lại gọi action tool. | Không dùng tool cho out-of-scope; trả lời/refuse theo prompt. |

## B3. Team eval cases

Team eval có đúng 10 case: 5 single-turn và 5 multi-turn. Đã có group run v3 bằng Groq, nhưng chỉ đo được 7/10 case do 3 provider errors; cần rerun bằng OpenRouter trước khi dùng metric trong report.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01 | URL OpenAI có phải nguồn official. | `source_check` với URL OpenAI. | Pending group run |
| G02 | Phân biệt kiểm tra provenance với đọc paper. | `source_check` với URL arXiv. | Pending group run |
| G03 | Không tự khẳng định uy tín domain chưa trong allowlist. | `source_check` với URL unknown. | Pending group run |
| G04 | Thiếu URL để kiểm tra nguồn. | `clarify(response_type="text")`. | Pending group run |
| G05 | Hỏi capability của tool. | Không gọi tool. | Pending group run |
| GM01 | Carry handle và limit sau correction. | `timeline(screenname="AndrewYNg", limit=7)`. | PASS trong measured subset |
| GM02 | Đổi từ kiểm tra nguồn sang đọc URL. | `fetch` URL Anthropic. | PASS trong measured subset |
| GM03 | URL được sửa ở lượt cuối. | `source_check` URL OpenAI mới. | PASS trong measured subset |
| GM04 | Confirmation trước Telegram action. | `clarify(response_type="yes_no")`. | Provider error; rerun required |
| GM05 | Đổi từ social sang web news. | `lookup(query="Gemini AI", topic="news", timeframe="week")`. | Provider error; rerun required |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| `Tin AI hôm nay` | `ui_live` | `lookup` | `transcripts/ui_live_openrouter_20260729T154945066376.transcript.json` | Agent answered và lưu tool trace. |
| Missing handle | Pending | Expected `clarify` rồi `timeline` sau khi user bổ sung. | Pending TV3 | Pending |
| Sensitive action | Pending | Expected `clarify(yes_no)` trước `send`. | Pending TV3 | Pending |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `tools/source_check/tool.py`, `tools/source_check/TOOL.md` | Direct smoke check URL OpenAI trả `domain=openai.com`, `source_type=official`. | Không fetch URL và không tự khẳng định nội dung trang đáng tin. |
| Core research tools | Run v0 OpenRouter | `lookup`, `fetch`, `timeline` và `social_search` có tool results trong run thật. | API quota/rate limit cần kiểm tra trước demo. |
| Optional built-in | `tools/send/tool.py` | Có dry-run/confirmation boundary. | Không live-send trong eval; v0 cho thấy cần cô lập/guardrail tốt hơn. |
| Bonus: tool mới thứ 4 trở đi | — | Chưa claim bonus. | Không ghi bonus khi chưa có >3 tool mới. |

## B6. Reflection

- `system_prompt.md` nên chịu trách nhiệm về scope, hỏi lại khi thiếu thông tin, confirmation trước action và quy tắc giữ đúng intent/query.
- `tools.yaml` nên nêu rõ khi nào dùng/không dùng từng tool, conventions cho `lookup.topic`, `timeframe`, `timeline.screenname` và điều kiện dùng `send`.
- Lỗi tool execution/rate limit phải review thủ công; routing PASS không tự chứng minh API thực thi đúng.
- Tiếp theo: rerun group eval v3 bằng OpenRouter, hoàn thiện transcript demo/UI public URL và cập nhật các outcome còn pending.
