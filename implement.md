# implement.md

## Công cụ này có khó không?

**Không quá khó nếu làm theo MVP từng bước.**  
Mức độ thực tế: **Trung bình nhẹ** cho QA có AI coding assistant hỗ trợ.

Lý do:
- Tool chỉ cần đọc file YAML, gọi API, so sánh kết quả, rồi in báo cáo.
- Phần dễ: Exact Match, Keyword Match, báo cáo console.
- Phần khó hơn: Smart AI Judge và xử lý nhiều kiểu response JSON khác nhau.

Cách làm tốt nhất: **xây MVP đơn giản trước**, chạy được end-to-end, sau đó mới nâng cấp.

---

## 1. Cách tiếp cận build tool

Ta sẽ xây một CLI tool bằng **Python**.

CLI nghĩa là QA chạy tool bằng Terminal, ví dụ:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

Luồng xử lý đơn giản:

```text
Đọc config API
→ Đọc file testcase YAML
→ Với từng testcase:
   → Gửi input tới API AI mục tiêu
   → Lấy actual output từ JSON response
   → Chấm điểm bằng 1 trong 3 cách:
      1. Exact Match
      2. Keyword Match
      3. Smart AI Judge
   → Lưu kết quả
→ In báo cáo tổng kết ra console
```

Nguyên tắc build:

1. **Không làm UI.**
2. **Không làm database.**
3. **Không làm export Excel ở MVP.**
4. **Chỉ tập trung chạy được API test từ YAML và in report rõ ràng.**

---

## 3. Dependencies tối thiểu

Trong `requirements.txt`:

```txt
requests
PyYAML
pytest
python-dotenv
```

Giải thích:

| Package | Dùng để làm gì |
|---|---|
| `requests` | Gọi REST API |
| `PyYAML` | Đọc file YAML |
| `pytest` | Viết test nhỏ |
| `python-dotenv` | Đọc API key từ file `.env` nếu cần |

---

## 5. Format config YAML đề xuất

File: `examples/config.yaml`

```yaml
target_api:
  url: "https://api.example.com/chat"
  method: "POST"
  timeout_seconds: 30

  headers:
    Authorization: "Bearer ${TARGET_API_KEY}"
    Content-Type: "application/json"

  body_template:
    message: "{{input}}"

  response_path: "data.answer"

judge_api:
  enabled: true
  url: "https://api.openai.com/v1/chat/completions"
  method: "POST"
  timeout_seconds: 60

  headers:
    Authorization: "Bearer ${JUDGE_API_KEY}"
    Content-Type: "application/json"

  model: "gpt-4o-mini"
```

Ý nghĩa:

| Field | Ý nghĩa |
|---|---|
| `target_api.url` | API của sản phẩm AI cần test |
| `target_api.headers` | Header khi gọi API |
| `target_api.body_template` | Body gửi đi, `{{input}}` sẽ được thay bằng câu hỏi testcase |
| `target_api.response_path` | Đường dẫn để lấy câu trả lời trong JSON response |
| `judge_api` | API của AI dùng làm giám khảo |

Ví dụ response:

```json
{
  "data": {
    "answer": "Xin chào, tôi có thể giúp gì cho bạn?"
  }
}
```

Với response này thì:

```yaml
response_path: "data.answer"
```

---

## 6. Ba phương pháp evaluation

> **Lưu ý quan trọng**: Công cụ sẽ không áp dụng tất cả các phương pháp cùng một lúc cho một testcase. Việc chọn lựa phương pháp chấm điểm nào sẽ do QA thiết lập thủ công thông qua trường `checking_method` trong file YAML, hoặc (ở các phiên bản nâng cấp sau) hệ thống sẽ tự động phân tích ngữ cảnh để quyết định phương pháp đánh giá phù hợp nhất.

### 6.1 Exact Match

Mục tiêu: câu trả lời thực tế phải giống expected 100%.

Cách làm đơn giản:

```text
Nếu actual_output == expected
→ PASS

Nếu khác
→ FAIL
```

Nên strip khoảng trắng đầu/cuối để tránh lỗi nhỏ:

```text
actual_output.strip() == expected.strip()
```

Kết quả reason mẫu:

```text
PASS: Actual output khớp chính xác với expected.
FAIL: Actual output không khớp expected.
```

---

### 6.2 Keyword Match

Mục tiêu: actual output phải chứa đủ các keyword bắt buộc.

Cách làm đơn giản:

```text
Với từng keyword trong testcase:
  Nếu keyword không xuất hiện trong actual output:
    FAIL
Nếu tất cả keyword đều xuất hiện:
  PASS
```

Nên so sánh không phân biệt hoa/thường:

```text
"Hoàn Tiền" và "hoàn tiền" được xem là giống nhau.
```

Kết quả reason mẫu:

```text
PASS: Tìm thấy tất cả từ khóa bắt buộc.
FAIL: Không tìm thấy từ khóa mong đợi '7 ngày'.
```

---

### 6.3 Smart AI Judge

Mục tiêu: dùng một AI khác làm giám khảo để đánh giá chất lượng câu trả lời.

Input gửi cho AI Judge gồm 3 phần:

```text
1. Câu hỏi gốc
2. Expected result
3. Actual output từ AI mục tiêu
```

Prompt cho Judge nên yêu cầu trả JSON cố định:

```text
Bạn là QA judge. Hãy đánh giá câu trả lời của AI mục tiêu.

Chỉ trả về JSON hợp lệ, không markdown.

Question:
{{input}}

Expected:
{{expected}}

Actual:
{{actual_output}}

Hãy trả về format:
{
  "status": "PASS" | "WARNING" | "FAIL",
  "reason": "lý do ngắn gọn, rõ ràng bằng tiếng Việt"
}

Quy tắc:
- PASS nếu actual đúng ý expected và không có rủi ro đáng kể.
- WARNING nếu đúng một phần, thiếu nhẹ, hoặc có thông tin thừa có thể gây hiểu nhầm.
- FAIL nếu sai, lạc đề, hoặc thiếu ý quan trọng.
```

Mapping kết quả:

| Judge trả về | Tool ghi nhận |
|---|---|
| `PASS` | PASS |
| `WARNING` | WARNING |
| `FAIL` | FAIL hoặc Fail Low Quality |

Nếu Judge API lỗi hoặc trả JSON sai format, MVP nên đánh dấu:

```text
FAIL: Smart AI Judge failed or returned invalid response.
```

---

## 7. Error handling bắt buộc theo PRD

Tool cần xử lý các trường hợp sau.

### 7.1 File testcase thiếu, trống hoặc sai YAML

Hành động:

```text
Dừng toàn bộ process.
```

Log:

```text
[ERROR] Không tìm thấy test case hoặc file sai định dạng. Vui lòng kiểm tra lại.
```

---

### 7.2 API target timeout

Hành động:

```text
Đánh dấu testcase hiện tại là Fail Timeout.
Chạy tiếp testcase kế tiếp.
```

Log:

```text
[WARN] API Timeout. AI không phản hồi trong thời gian giới hạn.
```

Status nên dùng:

```text
FAIL
```

Reason:

```text
Fail Timeout: API target không phản hồi trong thời gian giới hạn.
```

---

### 7.3 API target trả HTTP error

Ví dụ: `500`, `401`, `403`.

Hành động:

```text
Đánh dấu testcase hiện tại là Fail API Error.
Chạy tiếp testcase kế tiếp.
```

Log:

```text
[WARN] API Error: Hệ thống trả về mã lỗi [HTTP Status Code].
```

Reason mẫu:

```text
Fail API Error: HTTP 401.
```

---

### 7.4 Keyword Match thiếu keyword

Hành động:

```text
Đánh dấu testcase là FAIL.
```

Log:

```text
[RESULT] Fail: Không tìm thấy từ khóa mong đợi '[Keyword]'.
```

---

### 7.5 Smart AI Judge đánh giá đúng một phần hoặc có rủi ro

Hành động:

```text
Đánh dấu testcase là WARNING.
```

Log:

```text
[RESULT] Warning: Câu trả lời tạm chấp nhận nhưng có rủi ro/thiếu sót. Lý do: [Reason]
```

---

### 7.6 Smart AI Judge đánh giá sai hoặc lạc đề

Hành động:

```text
Đánh dấu testcase là FAIL.
```

Log:

```text
[RESULT] Fail: Giám khảo AI xác định câu trả lời không chính xác. Lý do: [Reason]
```

---

## 8. Implementation phases

# Phase 0 — Setup project

## Goal

Tạo project Python tối thiểu chạy được.

## Files/folders cần tạo

```text
qa_tool/
qa_tool/__init__.py
qa_tool/__main__.py
qa_tool/cli.py
examples/
tests/
requirements.txt
README.md
```

## Prompt gửi AI coding assistant

```text
Hãy tạo skeleton cho một Python CLI project tên qa_tool.

Yêu cầu:
- Có package qa_tool.
- Có file __main__.py để chạy bằng: python -m qa_tool
- Có cli.py dùng argparse để nhận:
  --config
  --testcases
- Khi chạy, chỉ cần print ra đường dẫn config và testcases đã nhận.
- Tạo requirements.txt gồm requests, PyYAML, pytest, python-dotenv.
- Không thêm framework phức tạp.
```

## Kết quả mong đợi

Chạy được:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

Console in ra kiểu:

```text
Config file: examples/config.yaml
Testcases file: examples/testcases.yaml
```

## Cách verify thủ công

1. Mở Terminal ở thư mục project.
2. Chạy:

```bash
pip install -r requirements.txt
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

3. Nếu không lỗi import và có print ra đường dẫn là đạt.

---

# Phase 1 — Đọc config YAML và testcase YAML

## Goal

Tool đọc được file YAML và báo lỗi rõ nếu file sai.

## Files/folders cần tạo

```text
qa_tool/config_loader.py
qa_tool/testcase_loader.py
examples/config.yaml
examples/testcases.yaml
```

## Prompt gửi AI coding assistant

```text
Hãy implement config_loader.py và testcase_loader.py.

Yêu cầu:
- Dùng PyYAML.
- config_loader.load_config(path) trả về dict config.
- testcase_loader.load_testcases(path) trả về list testcase từ key "testcases".
- Nếu file không tồn tại, trống, YAML sai format, hoặc không có testcases:
  raise ValueError với message:
  "[ERROR] Không tìm thấy test case hoặc file sai định dạng. Vui lòng kiểm tra lại."
- Update cli.py để đọc config và testcases, sau đó print số lượng testcase.
- Giữ code đơn giản, dễ đọc cho QA mới học.
```

## Kết quả mong đợi

Console:

```text
Loaded config successfully.
Loaded 3 testcases.
```

Nếu file sai:

```text
[ERROR] Không tìm thấy test case hoặc file sai định dạng. Vui lòng kiểm tra lại.
```

## Cách verify thủ công

Chạy:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

Sau đó thử cố tình đổi tên file testcase sai:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/missing.yaml
```

Kỳ vọng: tool báo lỗi dễ hiểu.

---

# Phase 2 — Gọi API target

## Goal

Với mỗi testcase, tool gửi `input` tới API target và nhận JSON response.

## Files/folders cần tạo

```text
qa_tool/api_client.py
qa_tool/response_extractor.py
```

## Prompt gửi AI coding assistant

```text
Hãy implement api_client.py và response_extractor.py.

Yêu cầu api_client.py:
- Có function call_target_api(config, user_input).
- Lấy target_api từ config.
- Hỗ trợ method POST trước.
- Thay "{{input}}" trong body_template bằng user_input.
- Gửi request bằng requests.
- Dùng timeout_seconds từ config.
- Nếu timeout, raise TimeoutError.
- Nếu HTTP status >= 400, raise custom exception ApiError có status_code.

Yêu cầu response_extractor.py:
- Có function extract_response(json_data, response_path).
- response_path dạng dot path, ví dụ "data.answer" hoặc "choices.0.message.content".
- Hỗ trợ key dict và index list.
- Nếu không tìm thấy path, raise ValueError rõ ràng.

Update cli.py:
- Loop qua từng testcase.
- Gọi target API.
- Extract actual output.
- Print actual output ra console.
- Nếu timeout hoặc API error, không dừng toàn bộ, chỉ log warning và chạy testcase tiếp theo.
```

## Kết quả mong đợi

Với mỗi testcase:

```text
Running TC001 - Exact match greeting
Actual output: Xin chào! Tôi có thể giúp gì cho bạn?
```

Nếu timeout:

```text
[WARN] API Timeout. AI không phản hồi trong thời gian giới hạn.
```

Nếu HTTP error:

```text
[WARN] API Error: Hệ thống trả về mã lỗi 401.
```

## Cách verify thủ công

Dùng API thật nếu có.

Nếu chưa có API thật, nhờ AI assistant tạo một fake local API nhỏ bằng Flask hoặc FastAPI để test. Nhưng MVP chính không cần phụ thuộc Flask.

Prompt tạo fake API:

```text
Hãy tạo một file dev_fake_api.py dùng Python built-in http.server hoặc Flask đơn giản.
API POST /chat nhận JSON {"message": "..."} và trả về:
{
  "data": {
    "answer": "Echo: <message>"
  }
}
Dùng để QA test tool local.
```

---

# Phase 3 — Implement Exact Match và Keyword Match

## Goal

Tool chấm được 2 method đơn giản:

```text
exact_match
keyword_match
```

## Files/folders cần tạo

```text
qa_tool/evaluators.py
tests/test_evaluators.py
```

## Prompt gửi AI coding assistant

```text
Hãy implement evaluators.py.

Yêu cầu:
- Có function evaluate(testcase, actual_output).
- Nếu checking_method là "exact_match":
  - So sánh actual_output.strip() với expected.strip()
  - Trả dict gồm status và reason
- Nếu checking_method là "keyword_match":
  - Lấy list keywords từ testcase
  - So sánh không phân biệt hoa/thường
  - Nếu thiếu keyword nào thì FAIL và reason:
    "Không tìm thấy từ khóa mong đợi '<keyword>'."
  - Nếu đủ keyword thì PASS
- Nếu checking_method không hỗ trợ, trả FAIL với reason rõ ràng.
- Viết pytest unit tests cho exact_match và keyword_match.
```

## Kết quả mong đợi

Result object đơn giản:

```python
{
  "status": "PASS",
  "reason": "Actual output khớp chính xác với expected."
}
```

Hoặc:

```python
{
  "status": "FAIL",
  "reason": "Không tìm thấy từ khóa mong đợi '7 ngày'."
}
```

## Cách verify thủ công

Chạy unit test:

```bash
pytest
```

Chạy tool với testcase exact/keyword:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

Kỳ vọng console có kết quả PASS/FAIL.

---

# Phase 4 — Implement Smart AI Judge

## Goal

Tool gọi AI Judge để chấm testcase có:

```yaml
checking_method: smart_ai_judge
```

## Files/folders cần tạo

```text
qa_tool/judge_client.py
```

## Prompt gửi AI coding assistant

```text
Hãy implement judge_client.py để hỗ trợ Smart AI Judge.

Yêu cầu:
- Có function judge_answer(config, testcase, actual_output).
- Lấy judge_api từ config.
- Nếu judge_api.enabled không phải true, trả FAIL với reason "Smart AI Judge chưa được bật trong config."
- Gửi prompt gồm:
  Question, Expected, Actual.
- Yêu cầu judge trả JSON:
  {
    "status": "PASS" | "WARNING" | "FAIL",
    "reason": "..."
  }
- Parse JSON response.
- Nếu judge trả status ngoài PASS/WARNING/FAIL thì trả FAIL.
- Nếu judge API timeout hoặc lỗi HTTP thì trả FAIL với reason rõ.
- Không log API key.
- Update evaluators.py hoặc cli.py để gọi judge_client khi checking_method là smart_ai_judge.
```

## Kết quả mong đợi

Console:

```text
Running TC003 - Smart judge answer quality
Actual output: Bạn vào Cài đặt > Bảo mật > Đổi mật khẩu.
Result: PASS
Reason: Câu trả lời đúng với expected.
```

Hoặc:

```text
Result: WARNING
Reason: Câu trả lời đúng một phần nhưng thiếu bước xác nhận mật khẩu mới.
```

## Cách verify thủ công

1. Set API key trong môi trường:

```bash
export JUDGE_API_KEY="your-api-key"
```

2. Đảm bảo `examples/config.yaml` có judge API.
3. Chạy:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

Nếu chưa có judge API thật, tạm thời skip Smart Judge trong MVP hoặc mock response.

---

# Phase 5 — Report console

## Goal

In báo cáo dễ đọc sau khi chạy xong.

## Files/folders cần tạo

```text
qa_tool/report.py
```

## Prompt gửi AI coding assistant

```text
Hãy implement report.py.

Yêu cầu:
- Có function print_realtime_log(testcase_id, testcase_name, actual_output, status, reason).
- Có function print_summary_report(results).
- Summary gồm:
  - Tổng số testcase
  - Số PASS
  - Số WARNING
  - Số FAIL
  - Pass rate
- Detail từng testcase gồm:
  - ID/Name
  - Input
  - Expected
  - Actual Output
  - Status
  - Reason
- Với WARNING và FAIL, reason bắt buộc phải hiển thị rõ.
- Không dùng thư viện UI phức tạp. Plain text là đủ.
- Update cli.py để gom results và gọi print_summary_report ở cuối.
```

## Kết quả mong đợi

Ví dụ output:

```text
==============================
Execution Summary
==============================
Total: 3
PASS: 1
WARNING: 1
FAIL: 1
Pass Rate: 33.33%

==============================
Testcase Details
==============================

[TC001] Exact match greeting
Input: Xin chào
Expected: Xin chào! Tôi có thể giúp gì cho bạn?
Actual: Xin chào! Tôi có thể giúp gì cho bạn?
Status: PASS
Reason: Actual output khớp chính xác với expected.

[TC002] Keyword match refund policy
Input: Chính sách hoàn tiền là gì?
Expected: Câu trả lời cần nói về hoàn tiền trong 7 ngày
Actual: Bạn có thể yêu cầu hoàn tiền.
Status: FAIL
Reason: Không tìm thấy từ khóa mong đợi '7 ngày'.
```

## Cách verify thủ công

Chạy tool và kiểm tra:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

Checklist:

- Có tổng số testcase.
- Có PASS/WARNING/FAIL count.
- Có pass rate.
- Mỗi testcase có input, expected, actual, status.
- WARNING/FAIL có reason rõ ràng.

---

# Phase 6 — Hoàn thiện error handling

## Goal

Tool không crash lung tung. Lỗi nào cần dừng thì dừng, lỗi nào thuộc testcase thì đánh dấu FAIL và chạy tiếp.

## Files/folders cần sửa

```text
qa_tool/cli.py
qa_tool/api_client.py
qa_tool/testcase_loader.py
qa_tool/config_loader.py
qa_tool/judge_client.py
qa_tool/report.py
```

## Prompt gửi AI coding assistant

```text
Hãy review và hoàn thiện error handling theo PRD.

Yêu cầu:
1. File testcase thiếu, trống hoặc sai YAML:
   - Dừng toàn bộ process
   - In:
     [ERROR] Không tìm thấy test case hoặc file sai định dạng. Vui lòng kiểm tra lại.

2. Target API timeout:
   - Không dừng process
   - Mark testcase hiện tại FAIL
   - Reason: Fail Timeout: API target không phản hồi trong thời gian giới hạn.
   - Log:
     [WARN] API Timeout. AI không phản hồi trong thời gian giới hạn.

3. Target API trả HTTP error:
   - Không dừng process
   - Mark testcase hiện tại FAIL
   - Reason gồm HTTP status code
   - Log:
     [WARN] API Error: Hệ thống trả về mã lỗi [HTTP Status Code].

4. Keyword Match thiếu keyword:
   - Mark FAIL
   - Reason:
     Không tìm thấy từ khóa mong đợi '<keyword>'.

5. Smart AI Judge trả WARNING:
   - Mark WARNING
   - Reason lấy từ judge

6. Smart AI Judge trả FAIL:
   - Mark FAIL
   - Reason lấy từ judge

7. Không bao giờ print API key/token ra console.
```

## Kết quả mong đợi

Tool xử lý lỗi gọn, không bị crash khi chỉ một testcase lỗi API.

## Cách verify thủ công

Test các case sau:

1. Sai path testcase.
2. File YAML sai format.
3. API URL sai.
4. API key sai gây 401.
5. Timeout bằng cách set timeout rất thấp:

```yaml
timeout_seconds: 1
```

6. Keyword thiếu.
7. Smart Judge trả WARNING/FAIL.

---

# Phase 7 — README và example polish

## Goal

QA khác có thể đọc README và chạy tool được.

## Files/folders cần tạo/sửa

```text
README.md
examples/config.yaml
examples/testcases.yaml
.env.example
```

## Prompt gửi AI coding assistant

```text
Hãy viết README.md đơn giản cho QA không chuyên code.

README cần có:
- Tool này làm gì
- Cách setup Python virtual environment
- Cách install requirements
- Cách tạo config.yaml
- Cách tạo testcases.yaml
- Cách chạy command
- Ý nghĩa PASS/WARNING/FAIL
- Các lỗi thường gặp và cách xử lý
- Nhắc không commit API key thật

Tạo thêm .env.example với:
TARGET_API_KEY=
JUDGE_API_KEY=
```

## Kết quả mong đợi

QA mới có thể làm theo README và chạy tool.

## Cách verify thủ công

Đưa README cho một người khác trong team làm theo.  
Nếu họ chạy được mà không cần hỏi thêm nhiều, README đạt.

---

## 9. MVP scope

MVP nên bao gồm:

- Đọc config YAML.
- Đọc testcase YAML.
- Gọi target API bằng POST.
- Extract actual output bằng `response_path`.
- Chấm:
  - Exact Match
  - Keyword Match
  - Smart AI Judge
- In realtime log.
- In summary report ra console.
- Error handling theo PRD.

Không làm trong MVP:

- UI web.
- Excel export.
- Database.
- Parallel execution.
- Complex retry.
- Multi-step conversation.
- Authentication flow phức tạp.
- Test qua browser UI.

---

## 10. Phase 2 improvements sau MVP

Sau khi MVP chạy ổn, mới cân nhắc thêm:

1. **Export report**
   - Markdown
   - CSV
   - HTML

2. **Retry API**
   - Retry 1-2 lần nếu timeout hoặc 5xx.

3. **Environment support**
   - `dev`
   - `staging`
   - `production`

4. **More flexible payload**
   - Cho phép template JSON phức tạp hơn.

5. **Better judge prompt**
   - Cho phép rubric riêng từng testcase.

6. **Parallel run**
   - Chạy nhiều testcase cùng lúc để tiết kiệm thời gian.

7. **Tag/filter testcase**
   - Chạy theo tag như `smoke`, `regression`.

Ví dụ format sau này:

```yaml
testcases:
  - id: TC010
    name: Refund smoke test
    tags:
      - smoke
      - refund
    input: "Tôi muốn hoàn tiền"
    expected: "Có hướng dẫn điều kiện hoàn tiền"
    checking_method: smart_ai_judge
```

---

## 11. Command chuẩn nên hỗ trợ

MVP command:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml
```

Có thể thêm sau:

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml --verbose
```

```bash
python -m qa_tool --config examples/config.yaml --testcases examples/testcases.yaml --output report.md
```

Nhưng chưa cần ở MVP.

---

## 12. Checklist cuối trước khi xem MVP là hoàn thành

MVP chỉ được xem là xong khi:

- [ ] Chạy được bằng `python -m qa_tool`.
- [ ] Đọc được config YAML.
- [ ] Đọc được testcase YAML.
- [ ] Gọi được API target.
- [ ] Extract được actual output từ JSON.
- [ ] Exact Match chạy đúng.
- [ ] Keyword Match chạy đúng.
- [ ] Smart AI Judge chạy được hoặc có lỗi rõ ràng nếu chưa config.
- [ ] Có summary report.
- [ ] Có testcase details.
- [ ] WARNING/FAIL luôn có reason.
- [ ] Timeout không làm dừng toàn bộ run.
- [ ] HTTP error không làm dừng toàn bộ run.
- [ ] File testcase sai thì dừng và báo lỗi đúng PRD.
- [ ] Không print API key ra console.

---

## 13. Prompt tổng để nhờ AI assistant review code

Sau khi code xong MVP, paste prompt này:

```text
Hãy review project Python CLI này theo PRD.

Tập trung kiểm tra:
1. Có đúng luồng:
   read config → read testcases → call API → extract response → evaluate → report
2. Error handling có đúng PRD không
3. Có chỗ nào có thể crash khi API lỗi không
4. Có lộ API key/token ra log không
5. Code có đang quá phức tạp không
6. Có file/function nào nên đơn giản hóa không

Không refactor lớn nếu không cần.
Ưu tiên MVP chạy ổn, dễ hiểu cho QA.
```

---

## 14. Lời khuyên thực tế khi vibe code

- Làm từng phase nhỏ, đừng yêu cầu AI generate toàn bộ tool một lần.
- Sau mỗi phase phải chạy command verify.
- Nếu lỗi, copy nguyên error gửi lại AI assistant.
- Đừng thêm feature mới khi MVP chưa chạy end-to-end.
- Ưu tiên code dễ đọc hơn code “xịn”.
- Luôn giữ example config và testcase thật đơn giản.
- Không commit API key thật vào Git.
