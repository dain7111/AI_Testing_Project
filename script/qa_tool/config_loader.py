import yaml
import os
import re
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

def load_config(path):
    # Load các biến môi trường từ file .env nếu có
    load_dotenv()
    
    if not os.path.exists(path):
        raise ValueError("Không tìm thấy config file hoặc file sai định dạng. Vui lòng kiểm tra lại.")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Tự động map các biến môi trường dạng ${ENV_VAR} trong file yaml
    def replace_env(match):
        env_var = match.group(1)
        return os.environ.get(env_var, "")
        
    content = re.sub(r'\$\{([^}]+)\}', replace_env, content)
    
    try:
        config = yaml.safe_load(content)
        if not config:
             raise ValueError("Config file trống.")
        # Inject đường dẫn thư mục chứa config để resolve các path tương đối trong api_client
        config_dir = os.path.dirname(os.path.abspath(path))
        if "target_api" in config:
            config["target_api"]["_config_dir"] = config_dir
        return config
    except yaml.YAMLError:
        raise ValueError("Không tìm thấy config file hoặc file sai định dạng. Vui lòng kiểm tra lại.")
