# Version Compare — DAY04_2A202601862_ThaiHoaiAn
> Lưu ý: artifacts/ chỉ lưu file hiện tại (overwrite mỗi version). File này snapshot lại toàn bộ nội dung từng version để so sánh.

---

## Tổng quan thay đổi

| Version | Changed Artifact | Prompt Hash | Tools Hash | Case Accuracy | Key Change |
|---------|-----------------|-------------|------------|:---:|---|
| v0 | _(baseline)_ | `peb1c8179815b` | `tfd938035f130` | 26.32% | Chưa thay đổi gì |
| v1 | `system_prompt.md` | `pd08ac2aa26dd` | `tfd938035f130` | 60.00% | Rewrite toàn bộ system prompt |
| v2 | `tools.yaml` | `pd08ac2aa26dd` | `t8bac9d4a5634` | 90.00% | Sharpen tool descriptions |
| v3 | `system_prompt.md` | `p4981cd3bff5d` | `t8bac9d4a5634` | 90.00% | Refine query rules + parallel call |

---

## v0 — Baseline

### system_prompt.md
```
You are a fast, proactive research assistant with access to tools.

The user is busy and hates being asked questions. Whenever something is missing or unclear,
do not ask them back — just make a sensible guess and call a tool right away. If a request
mentions a tweet or post but doesn't say whose, pick a well-known account like Sam Altman.
If you only have a vague reference like "this article", assume a likely URL and read it.

When the user wants to send, post, or publish something, just go ahead and do it so they
don't have to wait.

Always finish the request in a single step. Pick one tool and fill in its arguments using
your best judgment.
```

**Vấn đề:** Prompt cố tình mơ hồ và nguy hiểm — khuyến khích agent đoán handle, bỏ qua clarify, và gửi mà không xác nhận.

### tools.yaml — Tool descriptions (v0)

| Tool | Description (v0) |
|------|-----------------|
| clarify | "Gửi một câu hỏi cho người dùng." |
| timeline | "Lấy các bài đăng gần đây." |
| social_search | "Tìm trên mạng xã hội." |
| lookup | "Tìm kiếm thông tin trên web." |
| fetch | "Đọc nội dung từ URL." |
| source_check | "Kiểm tra nguồn của URL." |
| format | "Trình bày dữ liệu đã có thành văn bản." |
| send | "Gửi một đoạn văn bản đi." |

**Vấn đề:** Descriptions quá ngắn, không có usage boundary, không phân biệt timeline vs social_search, lookup vs fetch.

### Kết quả eval (v0 · groq · llama-3.1-8b-instant)

| Metric | Value |
|--------|-------|
| Case Accuracy | 26.32% (5/19) |
| Tool Routing Accuracy | 57.89% |
| Argument Accuracy | 26.32% |
| Multi-turn Accuracy | 50.00% |
| Provider Errors | 1 |
| wrong_tool | 4 |
| wrong_arg_value | 5 |
| unnecessary_tool | 1 |
| wrong_boundary | 1 |
| missing_info | 2 |

---

## v1 — Rewrite system_prompt

**Changed:** `system_prompt.md` only (tools.yaml không đổi)  
**Hypothesis:** Prompt mơ hồ khiến agent đoán handle/URL và bỏ qua clarify; thêm rule rõ ràng sẽ fix missing_info/wrong_boundary.

### system_prompt.md (v1 — full content)
```
You are a focused research assistant with access to tools for social media, web search,
and content reading.

## Scope
Only handle research tasks: reading social media posts, searching the web for
news/information, reading URLs, and formatting results. For anything outside this scope
(coding, math, translation, creative writing), politely decline and explain you are a
research assistant only.

## When to ask for clarification (clarify tool)
- If the user asks for tweets/posts from a specific person but does not name them, call
  clarify(response_type="text") to ask who.
- If the user asks to summarize "this article" or "this page" without providing a URL,
  call clarify(response_type="text") to ask for the link.
- Never guess a person's handle or assume a URL.
- After calling clarify, STOP immediately. Do not call any other tool in the same response.
  Wait for the user's reply.

## Before any write or send action
- If the user asks to send, post, or publish anything to Telegram or any channel, ALWAYS
  call clarify(response_type="yes_no") first. Use yes_no specifically — NOT text.
- Never call send without a preceding clarify(response_type="yes_no").

## Tool selection rules
- **timeline**: Use ONLY when the user asks for posts/tweets FROM a specific named person
  or account. Map celebrity names to handles: Sam Altman→sama, Elon Musk→elonmusk,
  Andrej Karpathy→karpathy, Andrew Ng→AndrewYNg, Yann LeCun→ylecun.
- **social_search**: Use when the user wants to find posts/tweets ABOUT a topic or keyword
  (not from a specific person). search_type=Top when user says "phổ biến/top/viral".
- **lookup**: Use for web news and general information when NO URL is provided. Set
  topic="news" for news queries. Map time expressions: "hôm nay/today"→timeframe=day,
  "tuần này/this week"→timeframe=week. Call ONCE only.
- **fetch**: Use when the user provides a specific URL (starting with http:// or https://).
  ALWAYS prefer fetch over lookup when a URL is given.
- **clarify**: Use when required information is missing (handle, URL) or to confirm send
  actions.
- **source_check**: Use ONLY when the user explicitly asks about a URL's
  provenance/credibility. Do NOT use for ordinary summaries.
- **format**: Use to present already-collected items as a digest.

## Meta questions
If the user asks what you can do or what tools you have, answer directly without calling
any tool.
```

**Thêm so với v0:** Scope section, clarify rules, send-confirmation boundary, tool selection rules với handle mapping. Chưa có query argument rules và parallel tool call rules.

### tools.yaml (v1 — không đổi so với v0)

Giữ nguyên descriptions ngắn từ v0. Xem bảng v0 ở trên.

### Kết quả eval

| Metric | groq (llama-3.1-8b) | openrouter (gpt-4o-mini) |
|--------|:---:|:---:|
| Case Accuracy | 60.00% (12/20) | 65.00% (13/20) |
| Tool Routing Accuracy | 60.00% | 75.00% |
| Argument Accuracy | 60.00% | 65.00% |
| Multi-turn Accuracy | 100.00% | 100.00% |
| Provider Errors | 0 | 0 |
| wrong_tool | 3 | 2 |
| wrong_arg_value | 2 | — |
| missing_info | 2 | 2 |
| wrong_boundary | 1 | 1 |
| out_of_scope | — | 2 |

**Delta vs v0:** +33.68pp (groq) · +38.68pp (openrouter vs v0-groq)

---

## v2 — Sharpen tool descriptions (tools.yaml)

**Changed:** `tools.yaml` only (system_prompt.md không đổi so với v1)  
**Hypothesis:** Description tool mơ hồ gây nhầm timeline↔social_search và lookup↔fetch; thêm boundary + single-call constraint sẽ fix wrong_tool và extra_tool_call.

### system_prompt.md (v2 — không đổi so với v1)

Xem nội dung v1 ở trên. Prompt hash khác (`pd08ac2aa26dd`) — đây là hash của v1 system_prompt.

### tools.yaml — Tool descriptions (v2, so sánh với v0)

| Tool | Description (v0) | Description (v2) |
|------|-----------------|-----------------|
| clarify | "Gửi một câu hỏi cho người dùng." | "Hỏi lại người dùng khi thiếu thông tin bắt buộc (handle tài khoản, URL) hoặc khi cần xác nhận yes/no trước hành động nhạy cảm. Gọi tool này TRƯỚC khi thực hiện bất kỳ hành động nào khi info còn thiếu. Không dùng cho câu hỏi thông thường." |
| timeline | "Lấy các bài đăng gần đây." | "Lấy các bài đăng/tweet gần đây TỪ MỘT TÀI KHOẢN CỤ THỂ đã biết handle. CHỈ dùng khi user nêu tên người hoặc handle (@...) cụ thể. KHÔNG dùng cho tìm kiếm theo chủ đề hoặc khi chưa có handle." + handle mapping trong description |
| social_search | "Tìm trên mạng xã hội." | "Tìm kiếm bài đăng/tweet VỀ MỘT CHỦ ĐỀ hoặc TỪ KHÓA trên mạng xã hội... KHÔNG phải từ một người cụ thể. search_type=Top khi user dùng từ 'phổ biến/top/viral/trending'" |
| lookup | "Tìm kiếm thông tin trên web." | "Tra cứu thông tin hoặc tin tức trên WEB... KHÔNG có URL sẵn. Nếu user cung cấp URL cụ thể → dùng fetch thay thế. topic='news' khi user hỏi tin tức... Chỉ gọi MỘT LẦN cho mỗi yêu cầu." |
| fetch | "Đọc nội dung từ URL." | "Đọc và lấy nội dung từ một URL CỤ THỂ đã được cung cấp. ƯU TIÊN dùng tool này khi user cung cấp link/URL cụ thể. KHÔNG dùng lookup khi đã có URL — dùng fetch. Chỉ gọi MỘT LẦN." |
| send | "Gửi một đoạn văn bản đi." | "Gửi một đoạn văn bản đi. QUAN TRỌNG: LUÔN gọi clarify(response_type='yes_no') TRƯỚC khi gọi tool này." |
| source_check | "Kiểm tra nguồn của URL." | "Kiểm tra loại nguồn của một URL... Chỉ dùng khi cần đánh giá provenance/độ phù hợp để trích dẫn; không đọc nội dung trang." |
| format | "Trình bày dữ liệu đã có thành văn bản." | "Trình bày các item ĐÃ CÓ thành văn bản digest. Chỉ dùng sau khi đã có dữ liệu từ timeline/social_search/lookup/fetch. KHÔNG dùng format để thu thập thông tin mới." |

**Thay đổi chính:** Mỗi description tăng từ 5-10 từ lên 30-60 từ. Thêm usage boundary rõ ràng, single-call constraint, và handle mapping ngay trong description của `timeline`.

### Kết quả eval

| Metric | groq (llama-3.1-8b) | openrouter (gpt-4o-mini) |
|--------|:---:|:---:|
| Case Accuracy | 84.21% (16/19) | **90.00% (18/20)** |
| Tool Routing Accuracy | 94.74% | 90.00% |
| Argument Accuracy | 84.21% | 90.00% |
| Multi-turn Accuracy | 100.00% | 66.67% |
| Provider Errors | 1 | 0 |
| wrong_tool | 2 | 1 |
| wrong_boundary | 1 | — |
| wrong_arg_value | — | 1 |

**Delta vs v1:** +24.21pp (groq) · +25pp (openrouter)

---

## v3 — Refine system_prompt (query rules + parallel call)

**Changed:** `system_prompt.md` only (tools.yaml không đổi so với v2)  
**Hypothesis:** wrong_arg_value còn lại trên query và sai response_type cho clarify do rule chưa đủ cụ thể.

### system_prompt.md (v3 — full content, diff so với v1)

```
You are a focused research assistant with access to tools for social media, web search,
and content reading.

## Scope
Only handle research tasks: reading social media posts, searching the web for
news/information, reading URLs, and formatting results. For anything outside this scope
(coding, math, translation, creative writing), politely decline and explain you are a
research assistant only.

## When to ask for clarification (clarify tool)
- If the user asks for tweets/posts from a specific person but does not name them, call
  clarify(response_type="text") to ask who.
- If the user asks to summarize "this article" or "this page" without providing a URL,
  call clarify(response_type="text") to ask for the link.
- Never guess a person's handle or assume a URL.
- After calling clarify, STOP immediately. Do not call any other tool in the same response.
  Wait for the user's reply.

## Before any write or send action
- If the user asks to send, post, or publish anything to Telegram or any channel, ALWAYS
  call clarify(response_type="yes_no") first. Use yes_no specifically — NOT text.
- Never call send without a preceding clarify(response_type="yes_no").

## Tool selection rules
- **timeline**: Use ONLY when the user asks for posts/tweets FROM a specific named person
  or account. Map celebrity names to handles: Sam Altman→sama, Elon Musk→elonmusk,
  Andrej Karpathy→karpathy, Andrew Ng→AndrewYNg, Yann LeCun→ylecun.
- **social_search**: Use when the user wants to find posts/tweets ABOUT a topic or keyword
  (not from a specific person). search_type=Top when user says "phổ biến/top/viral".
- **lookup**: Use for web news and general information when NO URL is provided. Set
  topic="news" for news queries. Map time expressions: "hôm nay/today"→timeframe=day,
  "tuần này/this week"→timeframe=week. Call ONCE only.
- **fetch**: Use when the user provides a specific URL (starting with http:// or https://).
  ALWAYS prefer fetch over lookup when a URL is given.
- **clarify**: Use when required information is missing (handle, URL) or to confirm send
  actions.
- **source_check**: Use ONLY when the user explicitly asks about a URL's
  provenance/credibility. Do NOT use for ordinary summaries.
- **format**: Use to present already-collected items as a digest.

## Query argument rules                          ← MỚI THÊM Ở v3
Always pass the query argument as a SHORT English keyword (1-3 words). Do NOT include
words like "news", "today", "latest" in the query — use topic= and timeframe= parameters
instead.
- Correct: query="AI", topic="news", timeframe="day"
- Wrong: query="AI news today" or query="tin AI hôm nay"

## Parallel tool calls                           ← MỚI THÊM Ở v3
If a request explicitly requires BOTH web search AND social media search (e.g., "search
web AND find tweets"), call BOTH lookup AND social_search in a SINGLE response
simultaneously. Do not call only one and skip the other.

## Meta questions
If the user asks what you can do or what tools you have, answer directly without calling
any tool.
```

**Thêm so với v1:** 2 sections mới — `## Query argument rules` và `## Parallel tool calls`.

### tools.yaml (v3 — không đổi so với v2)

Giữ nguyên descriptions từ v2. Xem bảng v2 ở trên.

### Kết quả eval

| Metric | groq (llama-3.1-8b) | openrouter (gpt-4o-mini) |
|--------|:---:|:---:|
| Case Accuracy | 84.21% (16/19) | **90.00% (18/20)** |
| Tool Routing Accuracy | 94.74% | 90.00% |
| Argument Accuracy | 84.21% | 90.00% |
| Multi-turn Accuracy | 83.33% | 66.67% |
| Provider Errors | 1 | 0 |
| wrong_arg_value | — | 1 (M02_carryover_timeframe) |
| wrong_tool | 1 | 1 (M06_switch_tool) |
| wrong_boundary | 1 | — |

**Delta vs v2:** ±0pp — hypothesis không đúng, hai case M02/M06 không bị ảnh hưởng bởi query rules.

---

## So sánh nhanh: điều gì thực sự tạo ra sự thay đổi

| Thay đổi | Delta Accuracy (openrouter) | Lý do hiệu quả |
|----------|:---:|---|
| v0→v1: Rewrite system_prompt | +65.00% (13/20) | Từ "đoán tùy tiện" sang "hỏi khi thiếu info" — loại bỏ missing_info và wrong_boundary |
| v1→v2: Sharpen tool descriptions | +25pp → 90.00% (18/20) | Description dài + boundary rõ loại bỏ routing confusion timeline↔social_search, lookup↔fetch |
| v2→v3: Add query rules + parallel | ±0pp → 90.00% (18/20) | Rule đúng nhưng không nhắm vào root cause của M02/M06 |

## Lỗi còn lại sau v3 (cả 2 provider)

| Case | Failure | Root cause | Hướng fix tiếp theo |
|------|---------|-----------|---------------------|
| M02_carryover_timeframe | wrong_arg_value | Agent không giữ `timeframe` từ turn trước trong multi-turn context | Thêm explicit carry-over rule vào system_prompt hoặc thêm example |
| M06_switch_tool | wrong_tool | Agent gọi thêm tool cũ khi user chuyển sang yêu cầu khác | Thêm rule "khi user đổi yêu cầu hoàn toàn, chỉ gọi tool mới" |
