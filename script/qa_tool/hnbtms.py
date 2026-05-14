import yaml
import json
import requests
import uuid
import os
import time
from datetime import datetime

# Define API Constants
API_URL = "https://btmsapiv2.tourvis.com/user/chat/messages"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi,en-US;q=0.9,en;q=0.8",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDg2NTA0IiwiaWF0IjoxNzc4NzUxNjY2LCJleHAiOjE3Nzg3NTU1NjYsImNvbXBhbnlfaWQiOjIxNjksInVzZXJfdHlwZSI6ImN1c3RvbWVyIiwiaXNfYWRtaW4iOmZhbHNlfQ.zzH8tHz8-6zWfSkVbO0-Wssz1IK4_XvHqBHHWmKlb1k",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://btms.tourvis.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://btms.tourvis.com/",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

def call_api(chat_id, user_message):
    payload = {
        "chatId": str(chat_id),
        "userMessage": user_message
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "status_code": getattr(response, 'status_code', None) if 'response' in locals() else None}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run testcases against BTMS API")
    parser.add_argument("-i", "--input", required=True, help="Path to input YAML testcase file")
    parser.add_argument("-o", "--output-dir", default="results", help="Directory to save JSON results")
    args = parser.parse_args()

    # Load YAML
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        exit(1)
    
    test_cases = data.get("test_cases", [])
    if not test_cases:
        print("No 'test_cases' found in the YAML file.")
        exit(1)
    
    # Create output dir
    os.makedirs(args.output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(args.input))[0]
    output_file = os.path.join(args.output_dir, f"{base_name}_results_{timestamp}.json")
    
    results = []
    
    for item in test_cases:
        if "test_case" in item:
            tc = item["test_case"]
            tc_id = tc.get("id", "Unknown")
            print(f"Running Test Case: {tc_id}")
            
            chat_id = str(uuid.uuid4())
            user_message = tc.get("input", {}).get("user_message", "")
            
            print(f"  -> Input: {user_message}")
            api_response = call_api(chat_id, user_message)
            
            results.append({
                "type": "test_case",
                "id": tc_id,
                "name": tc.get("name"),
                "chatId": chat_id,
                "input": user_message,
                "api_response": api_response
            })
            time.sleep(1)
            
        elif "test_flow" in item:
            tf = item["test_flow"]
            tf_id = tf.get("id", "Unknown")
            print(f"Running Test Flow: {tf_id}")
            
            current_chat_id = None
            flow_results = {
                "type": "test_flow",
                "id": tf_id,
                "name": tf.get("name"),
                "turns": []
            }
            
            for turn in tf.get("turns", []):
                turn_num = turn.get("turn")
                print(f"  -> Turn {turn_num}")
                
                setup = turn.get("setup", {})
                if setup.get("session_state", {}).get("is_new_session"):
                    current_chat_id = str(uuid.uuid4())
                
                if not current_chat_id:
                    current_chat_id = str(uuid.uuid4())
                
                user_message = turn.get("input", "")
                print(f"     Input: {user_message}")
                
                api_response = call_api(current_chat_id, user_message)
                
                flow_results["turns"].append({
                    "turn": turn_num,
                    "chatId": current_chat_id,
                    "input": user_message,
                    "api_response": api_response
                })
                time.sleep(1)
                
            results.append(flow_results)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\nFinished! Results saved to {output_file}")
