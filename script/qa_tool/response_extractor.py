def extract_response(json_data, response_path):
    if not response_path:
        return str(json_data)
        
    parts = response_path.split(".")
    current = json_data
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            raise ValueError(f"Không tìm thấy đường dẫn '{response_path}' trong JSON response.")
            
    return str(current)
