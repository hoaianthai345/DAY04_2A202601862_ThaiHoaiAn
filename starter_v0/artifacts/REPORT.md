# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent có khả năng phân tích thông tin mạng xã hội, tổng hợp tin tức web, đọc trực tiếp tài liệu từ URL và thêm tính năng **kiểm tra độ uy tín của nguồn**.

**Link dùng thử (truy cập được trong showdown):**

> URL: http://localhost:8501

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy bài đăng gần đây của tài khoản | không |
| social_search | tìm kiếm bài đăng trên mạng xã hội | không |
| lookup | tìm kiếm thông tin thời sự trên web | không |
| fetch | đọc và trích xuất nội dung từ URL | không |
| format | định dạng lại thông tin thành markdown digest | không |
| source_check | kiểm tra mức độ uy tín và nguồn gốc của một URL | có |

## A3. Câu hỏi mẫu để thử

1. Tóm tắt 5 bài tweet mới nhất của Sam Altman giúp mình.
2. Tìm tin tức nổi bật về GPT-5 hôm nay và định dạng lại thành báo cáo.
3. Kiểm tra xem link https://openai.com/index/introducing-gpt-5 có phải là nguồn chính thức đáng tin cậy để trích dẫn không?

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Tìm tin tức kết hợp | `lookup` -> `format` | Tối ưu prompt để agent không dùng nhầm timeline khi hỏi tin chung | (điền sau) |
| Đổi URL giữa chừng (Multi-turn) | `clarify` -> `source_check` | Agent biết cập nhật ngữ cảnh URL mới nhất từ user qua nhiều lượt chat | (điền sau) |
| Phân biệt Đọc bài vs Kiểm tra nguồn | `source_check` thay vì `fetch` | Sửa mô tả tool để agent hiểu rõ khi nào cần "kiểm tra độ uy tín" thay vì chỉ "đọc nội dung" | (điền sau) |
---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
