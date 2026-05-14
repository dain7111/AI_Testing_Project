import requests
import json

class ApiError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(message)

def call_target_api(config, testcase):
    user_input = testcase.get("input", "")
    chat_history = testcase.get("chat_history", [])
    
    target_api = config.get("target_api", {})
    api_type = target_api.get("type", "http")
    
    if api_type == "script":
        import os
        import importlib.util
        
        script_path = target_api.get("script_path")
        func_name = target_api.get("function_name", "call_api")
        
        # Resolve path tương đối so với vị trí file config nếu có
        config_dir = target_api.get("_config_dir", "")
        if script_path and not os.path.isabs(script_path) and config_dir:
            script_path = os.path.normpath(os.path.join(config_dir, script_path))
        
        if not script_path or not os.path.exists(script_path):
            raise Exception(f"Không tìm thấy script: {script_path}")
            
        spec = importlib.util.spec_from_file_location("custom_api_script", script_path)
        custom_script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_script)
        
        func = getattr(custom_script, func_name, None)
        if not func:
            raise Exception(f"Không tìm thấy hàm {func_name} trong script {script_path}")
            
        session_id = testcase.get("session_id", "default_session")
        try:
            response = func(session_id, user_input)
            return response
        except Exception as e:
            raise Exception(f"Lỗi khi thực thi script external: {e}")

    url = target_api.get("url")
    method = target_api.get("method", "POST")
    timeout = target_api.get("timeout_seconds", 30)
    headers = target_api.get("headers", {})
    
    body_template = target_api.get("body_template", {})
    body_str = json.dumps(body_template).replace("{{input}}", user_input)
    body = json.loads(body_str)

    # Chèn lịch sử chat (Multi-turn) vào giữa system prompt và câu hỏi hiện tại
    if chat_history and "messages" in body and isinstance(body["messages"], list):
        current_msgs = body["messages"]
        new_msgs = []
        
        # 1. Giữ lại System Prompt nếu có
        if current_msgs and current_msgs[0].get("role") == "system":
            new_msgs.append(current_msgs[0])
            current_msgs = current_msgs[1:]
            
        # 2. Bơm toàn bộ lịch sử (chat_history) từ testcase vào
        new_msgs.extend(chat_history)
        
        # 3. Đưa câu hỏi hiện tại (user_input) vào vị trí cuối cùng
        new_msgs.extend(current_msgs)
        
        body["messages"] = new_msgs

    try:
        if method.upper() == "POST":
            response = requests.post(url, json=body, headers=headers, timeout=timeout)
        else:
            response = requests.get(url, params=body, headers=headers, timeout=timeout)
            
        if response.status_code >= 400:
            raise ApiError(response.status_code, f"API Error: Hệ thống trả về HTTP {response.status_code}.")
            
        return response.json()
    except requests.exceptions.Timeout:
        raise TimeoutError("API Timeout. AI không phản hồi trong thời gian giới hạn.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối mạng: {str(e)}")
