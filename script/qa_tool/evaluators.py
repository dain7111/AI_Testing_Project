from .judge_client import judge_answer

def evaluate(testcase, actual_output, config=None):
    checking_method = testcase.get("checking_method")
    expected = str(testcase.get("expected", ""))
    actual = str(actual_output)
    
    if checking_method == "exact_match":
        if actual.strip() == expected.strip():
            return {"status": "PASS", "reason": "Actual output khớp chính xác với expected."}
        else:
            return {"status": "FAIL", "reason": "Actual output không khớp expected."}
            
    elif checking_method == "keyword_match":
        keywords = testcase.get("keywords", [])
        missing_keywords = []
        actual_lower = actual.lower()
        
        for kw in keywords:
            if kw.lower() not in actual_lower:
                missing_keywords.append(kw)
                
        if missing_keywords:
            return {"status": "FAIL", "reason": f"Không tìm thấy từ khóa mong đợi '{missing_keywords[0]}'."}
        else:
            return {"status": "PASS", "reason": "Tìm thấy tất cả từ khóa bắt buộc."}
            
    elif checking_method == "smart_ai_judge":
        if not config:
            return {"status": "FAIL", "reason": "Thiếu config để chạy Smart AI Judge."}
        return judge_answer(config, testcase, actual_output)
        
    else:
        return {"status": "FAIL", "reason": f"Phương pháp '{checking_method}' không được hỗ trợ."}
