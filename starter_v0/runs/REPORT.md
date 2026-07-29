## Tóm tắt kết quả theo version

| Version | Provider | Model | Case Accuracy | Routing Acc | Arg Acc | Multi-turn Acc | Pass/Total | Provider Errors |
|---------|----------|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| v0 | groq | llama-3.1-8b-instant | 26.32% | 57.89% | 26.32% | 50.00% | 5/19 | 1 |
| v1 | groq | llama-3.1-8b-instant | 60.00% | 60.00% | 60.00% | 100.00% | 12/20 | 0 |
| v1 | openrouter | gpt-4o-mini | 65.00% | 75.00% | 65.00% | 100.00% | 13/20 | 0 |
| v2 | groq | llama-3.1-8b-instant | 84.21% | 94.74% | 84.21% | 100.00% | 16/19 | 1 |
| v2 | openrouter | gpt-4o-mini | **90.00%** | **90.00%** | **90.00%** | 66.67% | 18/20 | 0 |
| v3 | groq | llama-3.1-8b-instant | 84.21% | 94.74% | 84.21% | 83.33% | 16/19 | 1 |
| v3 | openrouter | gpt-4o-mini | **90.00%** | **90.00%** | **90.00%** | 66.67% | 18/20 | 0 |

---

## Chi tiết từng version

### v0 — Baseline
- **Artifact version:** `v0+peb1c8179815b+tfd938035f130`
- **Changed:** _(baseline, chưa thay đổi gì)_
- **Hypothesis:** N/A
- **Result (groq):** 5/19 pass · 26.32% accuracy
- **Failure breakdown:**
  - `wrong_tool`: 4
  - `wrong_arg_value`: 5
  - `unnecessary_tool`: 1
  - `wrong_boundary`: 1
- **Nhận xét:** Model hoàn toàn không có ngữ cảnh rõ ràng — đoán handle tùy tiện, bỏ qua clarify, routing sai giữa timeline/social_search và lookup/fetch.

---

### v1 — Rewrite system_prompt
- **Artifact version:** `v1+pd08ac2aa26dd+tfd938035f130`
- **Changed:** `system_prompt.md`
- **Reason:** Thêm scope rules, clarify-when-missing, send-confirmation boundary, tool selection rules kèm handle mapping, English query rule.
- **Hypothesis:** Prompt mơ hồ khiến agent đoán handle/URL và bỏ qua clarify; thêm rule rõ ràng sẽ fix missing_info/wrong_boundary.
- **Result (groq):** 12/20 pass · 60.00% (+33.68pp vs v0)
- **Result (openrouter):** 13/20 pass · 65.00%
- **Failure breakdown (groq):**
  - `wrong_tool`: 3
  - `wrong_arg_value`: 2
  - `missing_info`: 2
  - `wrong_boundary`: 1
- **Nhận xét:** Cải thiện lớn. Multi-turn accuracy đạt 100% (groq). Còn sót wrong_tool giữa lookup/fetch và routing nhầm search_type arg.

---

### v2 — Sharpen tool descriptions (tools.yaml)
- **Artifact version:** `v2+pd08ac2aa26dd+t8bac9d4a5634`
- **Changed:** `tools.yaml`
- **Reason:** Viết lại toàn bộ description tool với usage boundary rõ ràng: timeline=người cụ thể/clarify nếu chưa có handle; fetch=ưu tiên khi có URL; lookup=không có URL/gọi một lần; send=luôn clarify trước.
- **Hypothesis:** Description tool mơ hồ gây nhầm timeline↔social_search và lookup↔fetch; thêm boundary + single-call constraint sẽ fix wrong_tool và extra_tool_call.
- **Result (groq):** 16/19 pass · 84.21% (+24.21pp vs v1-groq)
- **Result (openrouter):** 18/20 pass · 90.00% (+25pp vs v1-openrouter)
- **Failure breakdown (openrouter):**
  - `wrong_arg_value`: 1 (M02_carryover_timeframe)
  - `wrong_tool`: 1 (M06_switch_tool)
- **Nhận xét:** Bước nhảy lớn nhất trong toàn bộ quá trình. Tool descriptions rõ ràng giải quyết phần lớn routing confusion. OpenRouter không có provider error.

---

### v3 — Refine system_prompt (query rules + parallel call)
- **Artifact version:** `v3+p4981cd3bff5d+t8bac9d4a5634`
- **Changed:** `system_prompt.md`
- **Reason:** Thêm rule query=short-English-keyword (không dùng "AI news today", chỉ dùng "AI" + topic=news); enforce clarify(yes_no) vs clarify(text) cho send; tăng cường parallel tool call rule.
- **Hypothesis:** wrong_arg_value còn lại trên query và sai response_type cho clarify do rule chưa đủ cụ thể.
- **Result (groq):** 16/19 pass · 84.21% (±0 vs v2-groq, có 1 provider error)
- **Result (openrouter):** 18/20 pass · 90.00% (±0 vs v2-openrouter)
- **Failure breakdown (openrouter):**
  - `wrong_arg_value`: 1 (M02_carryover_timeframe)
  - `wrong_tool`: 1 (M06_switch_tool)
- **Nhận xét:** v3 không cải thiện accuracy so với v2 trên cả hai provider. Hai case fail (M02, M06) vẫn cố định — hypothesis chưa đúng hoặc cần thay đổi tools.yaml thêm.

---

## Phân tích lỗi còn lại (v3 openrouter)

| Case | Failure Type | Observed Mismatch | Mô tả |
|------|-------------|-------------------|-------|
| M02_carryover_timeframe | wrong_arg_value | extra_tool_call | Agent không carry over timeframe từ turn trước sang đúng arg |
| M06_switch_tool | wrong_tool | extra_tool_call | Agent gọi thêm tool không cần thiết khi user chuyển yêu cầu |

---

## Tiến trình cải thiện (groq baseline)

```
v0  ████░░░░░░░░░░░░░░░░  26.32%
v1  ████████████░░░░░░░░  60.00%
v2  ████████████████░░░░  84.21%
v3  ████████████████░░░░  84.21%  (không đổi)
```

```
v1 openrouter  █████████████░░░░░░░  65.00%
v2 openrouter  ██████████████████░░  90.00%
v3 openrouter  ██████████████████░░  90.00%  (không đổi)
```

---

## Kết luận

1. **Bước cải thiện lớn nhất** là v1 (rewrite system_prompt: +33pp) và v2 (sharpen tool descriptions: +24pp).
2. **OpenRouter/gpt-4o-mini vượt trội** so với groq/llama-3.1-8b-instant ở mọi version — không có provider error và accuracy cao hơn.
3. **v3 không mang lại cải thiện** — hai case M02 và M06 cần intervention khác: có thể sửa tool description carry-over context hoặc thêm example trong system_prompt.
4. **Bottleneck hiện tại:** multi-turn context carry-over (M02) và tool-switch logic (M06).
