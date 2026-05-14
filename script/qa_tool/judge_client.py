import json
import time
from openai import OpenAI
from openai import APIConnectionError, APITimeoutError, APIStatusError

def judge_answer(config, testcase, actual_output):
    judge_config = config.get("judge_api", {})
    if not judge_config.get("enabled", False):
        return {"status": "FAIL", "reason": "Smart AI Judge chưa được bật trong config."}
        
    timeout = judge_config.get("timeout_seconds", 60)
    model = judge_config.get("model", "gpt-4o-mini")
    
    api_key = judge_config.get("api_key", "")
    base_url = judge_config.get("base_url")
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=timeout
    )
    
    question = testcase.get("input", "")
    expected = testcase.get("expected", "")
    
    prompt = """Bạn là QA judge. Hãy đánh giá câu trả lời của AI mục tiêu.

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
- FAIL nếu sai, lạc đề, hoặc thiếu ý quan trọng."""

    prompt = prompt.replace("{{input}}", question)
    prompt = prompt.replace("{{expected}}", expected)
    prompt = prompt.replace("{{actual_output}}", actual_output)
    
    try:
        print(f"  [JUDGE] Sending request...")
        t_start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
            # NOTE: response_format json_object bị bỏ vì Kimi K2.5 không hỗ trợ -> gây hang
        )
        elapsed = time.time() - t_start
        print(f"  [JUDGE] Response received in {elapsed:.1f}s")
        content = response.choices[0].message.content
        
        # Xóa markdown json wrap nếu có
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        judge_result = json.loads(content.strip())
        
        status = judge_result.get("status", "FAIL")
        reason = judge_result.get("reason", "Judge did not provide a reason.")
        
        if status not in ["PASS", "WARNING", "FAIL"]:
            status = "FAIL"
            reason = f"Judge trả về status không hợp lệ: {status}"
            
        return {"status": status, "reason": reason}
        
    except APITimeoutError:
        return {"status": "FAIL", "reason": "Smart AI Judge API Timeout."}
    except APIStatusError as e:
        return {"status": "FAIL", "reason": f"Smart AI Judge API Error: HTTP {e.status_code}."}
    except APIConnectionError as e:
        return {"status": "FAIL", "reason": f"Lỗi kết nối Smart AI Judge: {str(e)}"}
    except json.JSONDecodeError:
        return {"status": "FAIL", "reason": "Smart AI Judge failed or returned invalid response format."}
    except Exception as e:
        return {"status": "FAIL", "reason": f"Lỗi xử lý Smart AI Judge: {str(e)}"}
