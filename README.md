# 🚀 AI Testing Framework - Project Overview

Tài liệu này cung cấp cái nhìn tổng quan về hệ thống **AI Testing Framework**, bao gồm các tính năng nổi bật, kiến trúc thư mục, và quy trình làm việc chuẩn (Workflow Process) dành cho team QA khi kiểm thử các dự án tích hợp AI.

---

## ✨ 1. Các Tính Năng Nổi Bật (Key Features)

- 🤖 **Agentic QA Automation:** Tích hợp sẵn các cấu hình Agent, Skills, và Workflows trong thư mục `.agents/` để hỗ trợ AI tự động hóa việc phân tích rủi ro và thiết kế testcase chuyên nghiệp.
- 📐 **Pattern-based Testing:** Framework được thiết kế dựa trên triết lý kiểm thử theo "Mẫu hành vi" (Pattern-based) với cơ chế đánh giá qua Confidence Score, phù hợp cho đặc tính non-deterministic (không xác định) của AI.
- 🛡️ **Bao Phủ Rủi Ro Toàn Diện:** Cung cấp bộ quy tắc bắt buộc để bao phủ không chỉ Functional mà còn các rủi ro đặc thù của AI như: *Hallucination*, *Prompt Injection / Security*, *Context Loss*, và *Toxicity*.
- 📂 **Tổ Chức Modular:** Tách biệt rõ ràng giữa các Rule cốt lõi, Kỹ năng tự động hóa (Skills) và không gian thực hành (Practices), giúp framework dễ dàng mở rộng cho nhiều mô hình AI khác nhau.

---

## 📁 2. Sơ Đồ Cấu Trúc Thư Mục (Directory Structure)

Dưới đây là sơ đồ kiến trúc và giải thích luồng hoạt động của hệ thống:

```text
AI_Testing/
├── .agents/                 # Não bộ tự động hóa: Cấu hình cho AI Agent/Assistant
│   ├── rules/               # Chứa các quy tắc bắt buộc (VD: manual-testcase-rule.md)
│   ├── skills/              # Chứa các kỹ năng để Agent thực thi nhiệm vụ
│   │   ├── requirement_analysis/ # Skill: Phân tích PRD để tìm rủi ro AI
│   │   └── generate_testcases/   # Skill: Tạo testcase chuẩn QA
│   └── workflows/           # Chứa các luồng quy trình làm việc tự động
├── practices/               # Khu vực thực hành và lưu trữ dự án thực tế
│   ├── requirement/         # Lưu trữ requirements đã sinh
│   └── testcase/            # Lưu trữ testcase đã sinh
├── README.md                # Giới thiệu chung và nguyên tắc cốt lõi (Core Principles)
└── PROJECT_OVERVIEW.md      # File tổng quan này (Features, Structure, Workflow)
```

### 🔍 Giải thích chi tiết các thư mục:

1. **`/.agents/`** 
   - **`rules/`**: Nơi QA Lead định nghĩa các "luật chơi" (VD: Không dùng Exact Match). AI Assistant sẽ bắt buộc phải đọc và tuân thủ các rule này.
   - **`skills/`**: Đóng gói các kỹ năng. Ví dụ khi bạn bảo AI "Hãy phân tích yêu cầu này", AI sẽ chạy skill `requirement_analysis` để rà soát Hallucination.
   - **`workflows/`**: Nơi định nghĩa các bước tuần tự (step-by-step) cho một quy trình lớn.
2. **`/practices/`**: Nơi áp dụng Framework vào thực tế. Mỗi dự án AI mới (ví dụ Chatbot du lịch, Hệ thống phân loại ảnh) sẽ có một thư mục riêng biệt trong này để chứa tài liệu Test Plan, Testcase, và Bug Reports.

---

## 🔄 3. Workflow Process (Hướng Dẫn Sử Dụng)

Khi tiếp nhận một tính năng AI mới để kiểm thử, QA Team vui lòng tuân thủ quy trình **4 Bước Tiêu Chuẩn** sau:

```text
┌───────────────────────────────────────────────────────────────────────┐
│  🤖 AI QA Workflow Process                                            │
│  ───────────────────────────────────────────────────────────────────  │
│  BƯỚC 1: Khởi tạo Workspace                                           │
│  (Tạo folder dự án → Thu thập PRD, API Docs, Prompts vào practices/)  │
│  ↓                                                                    │
│  BƯỚC 2: Phân Tích Rủi Ro & Lập Ma Trận                               │
│  (Chạy skill: ai_requirement_risk_analysis → Output: Risk Matrix)     │
│  ↓                                                                    │
│  BƯỚC 3: Thiết Kế Test Case Thông Minh                                │
│  (Chạy skill: generate_testcases → Thêm Anti-patterns)                │
│  ↓                                                                    │
│  BƯỚC 4: Thực Thi & Đánh Giá                                          │
│  (Chạy test UI/API → Đánh giá linh hoạt qua Confidence Score)         │
└───────────────────────────────────────────────────────────────────────┘
```
---

## 🤖 4. Tương Tác Cùng Antigravity

Framework này được thiết kế để hoạt động liền mạch với AI Assistant (Antigravity). Bạn không cần phải copy-paste lệnh (prompt) phức tạp, hệ thống sẽ tự vận hành:

1. **Tích hợp vào dự án:** Copy thư mục .agent vào thư mục gốc (root directory) của dự án đang làm việc.
2. **Bắt đầu trò chuyện với AI trên Antigravity:** Khi mở dự án lên Antigravity, AI tự động nhận diện thư mục .agent và sẽ áp dụng ngay các Rule, Skill, Workflow.
3. **Review & refine kết quả**: Sau khi Antigravity trả kết quả, nên kiểm tra lại và chỉnh sửa cho phù hợp với yêu cầu thực tế.

---

## 💡 Best Practices khi sử dụng Framework
- **Cập nhật Rules liên tục:** AI thay đổi rất nhanh. Nếu có kỹ thuật tấn công prompt mới, hãy đưa nó vào Rules để team tham khảo.
- **Tái sử dụng Prompts:** Lưu lại các bộ dữ liệu tấn công (Red Teaming payloads) để sử dụng chung cho nhiều dự án trong `/practices/`.
- **Tư duy Thám tử:** Đừng chỉ test đường màu hồng (Happy Path). Hãy nghĩ cách "bẫy" AI để nó bộc lộ điểm yếu!
