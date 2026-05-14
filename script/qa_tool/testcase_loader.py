import yaml

def load_testcases(path):
    with open(path, 'r', encoding='utf-8') as f:
        # Hỗ trợ YAML stream (nhiều block ngăn cách bằng '---')
        docs = list(yaml.safe_load_all(f))
        
    testcases = []
    for doc in docs:
        if not doc:
            continue
            
        # Hỗ trợ cả "testcases" (cũ) và "test_cases" (mới)
        root_list = doc.get("testcases") or doc.get("test_cases")
        if root_list and isinstance(root_list, list):
            for t in root_list:
                t["chat_history"] = t.get("chat_history", [])
                testcases.append(t)
        else:
            # Hỗ trợ định dạng mới chuẩn nghiệp vụ (tourvis_booking_flow.yaml)
            tc = {
                "id": doc.get("id", "UNKNOWN"),
                "name": doc.get("name", "Unnamed"),
                "checking_method": doc.get("checking_method", "keyword_match") # Tạm thời fallback về keyword_match
            }
            
            # Nếu dùng keyword_match, lấy danh sách keywords
            tc["keywords"] = doc.get("keywords", [])
            
            # Trích xuất câu hỏi
            user_input = doc.get("input", "")
            if isinstance(user_input, dict):
                tc["input"] = user_input.get("user_message", "")
            else:
                tc["input"] = str(user_input)
                
            # Trích xuất kết quả mong đợi
            expected = doc.get("expected", "")
            if not expected and "expected_output_pattern" in doc:
                expected = doc["expected_output_pattern"]
            tc["expected"] = str(expected)
            
            # Trích xuất Lịch sử chat (Multi-turn)
            setup = doc.get("setup", {})
            state = setup.get("session_state", {})
            history = state.get("chat_history", [])
            tc["chat_history"] = history
            
            testcases.append(tc)
            
    if not testcases:
        raise ValueError("Không tìm thấy testcase nào hợp lệ trong file.")
        
    return testcases
