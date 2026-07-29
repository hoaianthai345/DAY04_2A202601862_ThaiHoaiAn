# Role 2 — TV2: Eval & Tối ưu Agent

## Tổng quan

TV2 là người chịu trách nhiệm **đo lường và cải thiện chất lượng agent** thông qua vòng lặp evidence-driven: chạy eval → đọc log → đặt giả thuyết → sửa prompt/tool declaration → chạy lại. Toàn bộ quá trình phải có bằng chứng thật từ run JSON, không dựa vào cảm giác.

---

## Deliverables bắt buộc

| File | Mô tả |
| :--- | :--- |
| `runs/*.json` | File JSON mỗi lần chạy eval (v0, v1, v2, v3, group) |
| `artifacts/system_prompt.md` | Bản prompt cuối sau 3 vòng tối ưu |
| `artifacts/tools.yaml` | Khai báo tool cuối sau chỉnh sửa |
| `artifacts/version_log.csv` | Log giả thuyết và metric cho từng version |
| `data/eval_group.json` | Đúng 10 eval case do nhóm tự viết (5 single + 5 multi-turn) |

---

## Quy ước file — tránh conflict với TV1 và TV3

TV2 **sở hữu và chỉnh sửa** các file sau; TV1 và TV3 không chạm vào:

- `data/eval_group.json`
- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`
- `artifacts/version_log.csv`
- `runs/` (chỉ TV2 tạo run JSON)

> **Lưu ý:** Khi TV1 đổi tên tool mới, TV2 phải sync ngay vào `tools.yaml` và `system_prompt.md` để tránh eval báo `not declared`.

---

## Quy trình làm việc chi tiết

### Bước 0 — Nhận bàn giao từ TV1

Trước khi bắt đầu bất kỳ eval nào, chờ TV1 thông báo:
- Tên tool mới, schema (input/output), file `TOOL.md`
- Kết quả smoke-test tool đã chạy được chưa
- Provider đang dùng (openrouter hay khác)

Sau đó kiểm tra `tools/__init__.py` và `artifacts/tools.yaml` đã có tool mới chưa.

---

### Bước 1 — Chạy Baseline (v0)

```bash
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

**Không sửa bất kỳ thứ gì trước khi chạy v0.** Đây là baseline chuẩn để so sánh.

Sau khi chạy xong, đọc các trường quan trọng trong file `runs/v0_*.json`:

| Trường | Ý nghĩa |
| :--- | :--- |
| `summary.case_accuracy` | Tỷ lệ case đúng toàn phần |
| `summary.tool_routing_accuracy` | Tỷ lệ chọn đúng tool |
| `summary.argument_accuracy` | Tỷ lệ args đúng |
| `summary.multiturn_accuracy` | Tỷ lệ multi-turn đúng |
| `summary.provider_error_cases` | Số lỗi từ provider (phải = 0) |
| `summary.measured_cases` | Số case thực sự chấm (phải = total) |
| `results[*].result.failures` | Danh sách lỗi từng case |
| `results[*].result.observed_mismatch` | Tool/args thực tế vs. expected |

> **Điều kiện metric hợp lệ:** `provider_error_cases == 0` và `measured_cases == total_cases`.

Ghi dòng v0 vào `version_log.csv`:

```
v0,ThaiHoaiAn,system_prompt.md,v0,<prompt_hash>,<tools_hash>,baseline run,no change yet,case_accuracy,N/A,<giá_trị_v0>,runs/v0_*.json
```

---

### Bước 2 — Phân tích lỗi (Failure Analysis)

Với mỗi case fail trong v0, đọc kỹ:

1. `observed_mismatch` — agent gọi tool gì / args gì thực tế
2. `failures` — mô tả lý do chấm sai
3. `actual_tool_calls` — trace đầy đủ các bước agent
4. `tool_results` — tool trả về gì (lỗi thật hay kết quả thật)

Sau đó **phân loại lỗi** theo `failure_type`:

| Loại lỗi | Nguyên nhân thường gặp |
| :--- | :--- |
| `wrong_tool` | Prompt không phân biệt rõ khi nào dùng `timeline` vs `social_search` vs `lookup` |
| `wrong_arg_value` | Tool declaration không nêu convention (vd: `limit` mặc định, `timeframe` mapping) |
| `wrong_boundary` | Prompt không bắt buộc xác nhận trước action ghi (`send`) |
| `unnecessary_tool` | Prompt không có rule "trả lời thẳng nếu là câu hỏi meta" |
| `out_of_scope` | Prompt thiếu danh sách scope rõ ràng để từ chối |
| `missing_info` | Prompt không yêu cầu `clarify` khi thiếu handle/URL |

---

### Bước 3 — 3 vòng tối ưu (v1 → v2 → v3)

**Quy tắc:** Mỗi version chỉ được sửa **một thứ** — hoặc `system_prompt.md` hoặc `tools.yaml`. Không sửa cả hai cùng lúc. Không chạy hai version liên tiếp mà không đọc log.

#### Vòng v1

1. Chọn 1 lỗi phổ biến nhất từ v0.
2. Đặt giả thuyết cụ thể, ví dụ:
   *"Agent dùng `social_search` thay vì `timeline` vì mô tả tool không nêu khi nào dùng handle cụ thể."*
3. Sửa đúng chỗ đó trong `tools.yaml` hoặc `system_prompt.md`.
4. Chạy:
   ```bash
   python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
   ```
5. So sánh metric v1 vs v0, ghi vào `version_log.csv`.

#### Vòng v2

1. Đọc log v1. Tìm loại lỗi tiếp theo còn nhiều.
2. Đặt giả thuyết mới (khác v1).
3. Sửa một thứ, chạy lại:
   ```bash
   python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
   ```
4. Ghi log.

#### Vòng v3

1. Đọc log v2. Lấy case khó nhất còn lại.
2. Đặt giả thuyết thứ 3.
3. Sửa một thứ, chạy lại:
   ```bash
   python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
   ```
4. Ghi log.

> **Lưu ý quan trọng:** v1, v2, v3 phải là **3 cải tiến có hypothesis khác nhau và log thật**. Không được chạy lại cùng cấu hình chỉ để có tên v1/v2/v3.

---

### Bước 4 — Viết 10 Eval Case cho nhóm

File: `data/eval_group.json`
**Không dùng case mẫu trong `samples/eval_group.schema.example.json` — đó chỉ là tham khảo schema, không tính vào 10 case.**

#### Cấu trúc bắt buộc mỗi case

```json
{
  "id": "G01_<tên_ngắn>",
  "phase": "B",
  "failure_type": "<một_trong_6_loại>",
  "query": "<câu_hỏi_single_turn>",
  "expect": {
    "tool_calls": [{"name": "<tên_tool>", "args": {}}]
  },
  "metadata": {
    "what_it_tests": "<mô_tả_điều_case_này_kiểm_tra>"
  }
}
```

Với multi-turn, thay `query` bằng `turns`:

```json
{
  "id": "GM01_<tên_ngắn>",
  "phase": "B",
  "failure_type": "<một_trong_6_loại>",
  "turns": [
    {"role": "user", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "expect": {
    "tool_calls": [{"name": "<tên_tool>", "args": {}}]
  },
  "metadata": {
    "what_it_tests": "<mô_tả>"
  }
}
```

#### Phân bổ 10 case

| # | Loại | Gợi ý failure_type | Gợi ý scenario |
| :--- | :--- | :--- | :--- |
| G01 | Single-turn | `wrong_tool` | Từ khóa có thể nhầm `lookup` với `social_search` |
| G02 | Single-turn | `wrong_arg_value` | Argument nâng cao (vd: `format`, `count`) |
| G03 | Single-turn | `out_of_scope` | Yêu cầu ngoài phạm vi (vd: viết code, dịch thuật) |
| G04 | Single-turn | `wrong_boundary` | Hành động ghi nhưng không confirm |
| G05 | Single-turn | `missing_info` | Thiếu thông tin cần thiết để gọi tool |
| GM01 | Multi-turn | `missing_info` | Lượt 1 thiếu handle, lượt 2 bổ sung |
| GM02 | Multi-turn | `wrong_arg_value` | Sửa giá trị arg ở lượt sau (carry-over) |
| GM03 | Multi-turn | `wrong_tool` | Chuyển tool giữa các lượt (vd: Twitter → web) |
| GM04 | Multi-turn | `wrong_arg_value` | Sửa nhầm tên người sang đúng handle |
| GM05 | Multi-turn | `wrong_boundary` | Lượt 1 yêu cầu gửi, lượt 2 xác nhận |

> **Quy tắc multi-turn:** Phần tử **cuối** của `turns` phải là user turn đang được chấm (tức là turn mà agent cần trả lời đúng).

Sau khi viết xong 10 case, chạy group eval:

```bash
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

---

### Bước 5 — Cập nhật version_log.csv

Sau mỗi run, điền đầy đủ một dòng:

```
version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_name,metric_before,metric_after,run_file
```

Ví dụ:

```
v1,ThaiHoaiAn,tools.yaml,v1,abc123,def456,"timeline vs social_search ambiguous","Thêm mô tả khi nào dùng handle cụ thể vào tools.yaml",tool_routing_accuracy,0.62,0.77,runs/v1_base_20260729.json
```

---

## Format System Prompt tốt — Những điều cần lưu ý

Baseline `system_prompt.md` hiện tại có những vấn đề cố ý sau đây (phục vụ v0 để thấy lỗi):

- Khuyến khích "đoán bừa" khi thiếu thông tin → làm fail các case `missing_info`
- Bảo agent "tự gửi" mà không confirm → fail các case `wrong_boundary`
- Không có scope rõ ràng → fail các case `out_of_scope`
- Không phân biệt tool nào dùng khi nào → fail `wrong_tool`

Mỗi vòng sửa, chỉ xử lý **một vấn đề** và đo xem metric tương ứng có tăng không.

---

## Các lệnh hay dùng

```bash
# Chạy base eval
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json

# Chạy group eval
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json

# Parse run JSON thành CSV để phân tích
python scripts/parse_runs.py runs/ --output analysis/base_runs.csv

# Chat live để test thủ công
python chat.py --provider openrouter --version v3
```

---

## Checklist hoàn thành cho TV2

- [ ] Đã nhận bàn giao tool mới + provider config từ TV1
- [ ] Chạy v0 thành công, `provider_error_cases == 0`
- [ ] Đã đọc và phân tích log v0, xác định ít nhất 3 loại lỗi
- [ ] v1: 1 hypothesis → 1 thay đổi → đo metric → ghi log
- [ ] v2: 1 hypothesis mới → 1 thay đổi → đo metric → ghi log
- [ ] v3: 1 hypothesis mới → 1 thay đổi → đo metric → ghi log
- [ ] Viết đúng 10 group eval case (5 single + 5 multi-turn), chạy và lưu kết quả
- [ ] `version_log.csv` có đủ 4 dòng: v0, v1, v2, v3
- [ ] Bàn giao `artifacts/system_prompt.md` + `tools.yaml` bản cuối cho TV3 trước demo
- [ ] Sẵn sàng giải thích từng thay đổi hypothesis trong buổi demo (evidence từ log)
