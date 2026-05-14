import argparse
from .config_loader import load_config
from .testcase_loader import load_testcases
from .api_client import call_target_api, ApiError
from .response_extractor import extract_response
from .evaluators import evaluate
from .report import print_realtime_log, print_summary_report
import sys
import uuid

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description="QA Automation Tool for AI Testing")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--testcases", required=True, help="Path to testcases.yaml")
    
    args = parser.parse_args()
    
    try:
        config = load_config(args.config)
        testcases = load_testcases(args.testcases)
        
        response_path = config.get("target_api", {}).get("response_path", "")
        
        print(f"==========================================")
        print(f"Bắt đầu chạy {len(testcases)} testcases...\n")
        
        results = []
        
        for item in testcases:
            if "test_flow" in item:
                flow = item["test_flow"]
                flow_id = flow.get("id", "UNKNOWN_FLOW")
                flow_name = flow.get("name", "Unnamed Flow")
                print(f"\n>>> BẮT ĐẦU DYNAMIC FLOW [{flow_id}] - {flow_name} <<<")
                
                # Bộ nhớ lưu lịch sử động của Flow này
                dynamic_chat_history = []
                current_chat_id = str(uuid.uuid4())
                
                for turn in flow.get("turns", []):
                    turn_idx = turn.get("turn", 0)
                    desc = turn.get("description", "Unnamed Turn")
                    user_input = turn.get("input", "")
                    
                    print(f"\n--- Turn {turn_idx}: {desc} ---")
                    
                    # Convert 'expected' array to string
                    expected_raw = turn.get("expected", [])
                    expected_str = "\n".join([str(e) for e in expected_raw]) if isinstance(expected_raw, list) else str(expected_raw)
                    
                    # Khởi tạo lại lịch sử nếu có is_new_session: true
                    setup = turn.get("setup", {})
                    if setup.get("session_state", {}).get("is_new_session", False):
                        dynamic_chat_history = []
                        current_chat_id = str(uuid.uuid4())
                        
                    # Tạo Virtual Testcase để dùng lại các module API/Evalũ
                    tc_virtual = {
                        "id": f"{flow_id}_T{turn_idx}",
                        "name": desc,
                        "input": user_input,
                        "expected": expected_str,
                        "checking_method": "smart_ai_judge",
                        "chat_history": dynamic_chat_history.copy(), # Truyền lịch sử TÍCH LŨY THỰC TẾ
                        "session_id": current_chat_id # ID để dùng chung context cho script external
                    }
                    
                    actual_output = "N/A"
                    status = "FAIL"
                    reason = "Lỗi không xác định."
                    
                    try:
                        # 1. Gọi API (api_client sẽ tự chèn dynamic_chat_history vào messages)
                        json_response = call_target_api(config, tc_virtual)
                        
                        # 2. Bóc tách câu trả lời THỰC TẾ
                        actual_output = extract_response(json_response, response_path)
                        
                        # 3. Chấm điểm
                        eval_result = evaluate(tc_virtual, actual_output, config)
                        status = eval_result['status']
                        reason = eval_result['reason']
                        
                        # 4. QUAN TRỌNG: LƯU CÂU TRẢ LỜI THỰC TẾ VÀO BỘ NHỚ LỊCH SỬ CHO TURN SAU
                        dynamic_chat_history.append({"role": "user", "content": user_input})
                        dynamic_chat_history.append({"role": "assistant", "content": actual_output})
                        
                    except TimeoutError as e:
                        reason = "Fail Timeout: API target không phản hồi."
                    except ApiError as e:
                        reason = f"Fail API Error: HTTP {e.status_code}."
                    except Exception as e:
                        reason = f"Lỗi không mong đợi: {e}"
                        
                    print_realtime_log(tc_virtual["id"], tc_virtual["name"], actual_output, status, reason)
                    
                    results.append({
                        "id": tc_virtual["id"],
                        "name": tc_virtual["name"],
                        "input": user_input,
                        "expected": expected_str,
                        "actual": actual_output,
                        "status": status,
                        "reason": reason
                    })
            else:
                tc_id = item.get("test_case", item).get("id", "UNKNOWN")
                tc_name = item.get("test_case", item).get("name", "Unnamed")
                user_input = item.get("test_case", item).get("input", "")
                if isinstance(user_input, dict):
                    user_input = user_input.get("user_message", "")
                expected_raw = item.get("test_case", item).get("expected_output_pattern", [])
                expected = "\n".join([str(e) for e in expected_raw]) if isinstance(expected_raw, list) else str(expected_raw)
                
                actual_output = "N/A"
                status = "FAIL"
                reason = "Lỗi không xác định."
                
                tc_virtual = {
                    "id": tc_id,
                    "name": tc_name,
                    "input": user_input,
                    "expected": expected,
                    "checking_method": "smart_ai_judge",
                    "session_id": str(uuid.uuid4())
                }
                
                try:
                    json_response = call_target_api(config, tc_virtual)
                    actual_output = extract_response(json_response, response_path)
                    eval_result = evaluate(tc_virtual, actual_output, config)
                    status = eval_result['status']
                    reason = eval_result['reason']
                except TimeoutError as e:
                    reason = "Fail Timeout"
                except ApiError as e:
                    reason = f"Fail API Error: HTTP {e.status_code}."
                except Exception as e:
                    reason = f"Lỗi: {e}"
                    
                print_realtime_log(tc_id, tc_name, actual_output, status, reason)
                results.append({"id": tc_id, "name": tc_name, "input": user_input, "expected": expected, "actual": actual_output, "status": status, "reason": reason})
            
        # In báo cáo tổng hợp
        print_summary_report(results)
        
        # Xuất file CSV cho Excel
        # export_to_csv(results)
                
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Lỗi không xác định: {e}")
        return 1

    return 0

if __name__ == "__main__":
    main()
