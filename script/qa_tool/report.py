def print_realtime_log(testcase_id, testcase_name, actual_output, status, reason):
    print(f"Running [{testcase_id}] - {testcase_name}")
    print(f"  Actual output: {actual_output}")
    print(f"  Result: {status}")
    print(f"  Reason: {reason}\n")

def print_summary_report(results):
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    warning = sum(1 for r in results if r['status'] == 'WARNING')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print("==============================")
    print("Execution Summary")
    print("==============================")
    print(f"Total: {total}")
    print(f"PASS: {passed}")
    print(f"WARNING: {warning}")
    print(f"FAIL: {failed}")
    print(f"Pass Rate: {pass_rate:.2f}%")
    
    print("\n==============================")
    print("Testcase Details")
    print("==============================")
    
    for r in results:
        print(f"\n[{r['id']}] {r['name']}")
        print(f"Input: {r['input']}")
        print(f"Expected: {r['expected']}")
        print(f"Actual: {r['actual']}")
        print(f"Status: {r['status']}")
        print(f"Reason: {r['reason']}")

# import csv
# import os
# from datetime import datetime

# def export_to_csv(results, output_dir="."):
#     if not results:
#         return
        
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"test_report_{timestamp}.csv"
#     filepath = os.path.join(output_dir, filename)
    
#     # Sử dụng 'utf-8-sig' để Excel không bị lỗi font tiếng Việt
#     with open(filepath, mode='w', encoding='utf-8-sig', newline='') as file:
#         writer = csv.writer(file)
#         # Ghi dòng tiêu đề
#         writer.writerow(["Testcase ID", "Tên Testcase / Flow", "Câu hỏi (Input)", "Kỳ vọng (Expected)", "Thực tế (Actual)", "Kết quả (Status)", "Chi tiết / Lý do (Reason)"])
        
#         # Ghi dữ liệu
#         for r in results:
#             writer.writerow([r.get('id'), r.get('name'), r.get('input'), r.get('expected'), r.get('actual'), r.get('status'), r.get('reason')])
            
#     print(f"\n[INFO] Đã xuất báo cáo CSV thành công tại: {filepath}")
#     print(f"[INFO] (Bạn có thể mở file này trực tiếp bằng Excel)")
