# 🚀 Quickstart Guide: Sử dụng AI Testing Framework với Antigravity

Tài liệu này hướng dẫn bạn cách bắt đầu nhanh với **AI Testing Framework**, tận dụng sức mạnh của trợ lý AI (Antigravity) để tự động hóa quy trình phân tích và thiết kế kịch bản kiểm thử (testcase) cho ứng dụng AI.

---

## 1. 📁 Quy Định Đặt Tên (Naming Convention)

Để hệ thống lưu trữ nhất quán và Antigravity dễ dàng định vị, đọc hiểu ngữ cảnh, bạn **bắt buộc** tuân thủ các quy tắc đặt tên sau:

### Tên Thư Mục (Folder)
- **Cú pháp:** Viết thường (lowercase), sử dụng dấu gạch dưới `_` hoặc gạch ngang `-` để phân cách các từ. Tuyệt đối **không** dùng tiếng Việt có dấu, khoảng trắng hay ký tự đặc biệt.
- **Vị trí:** Tất cả các dự án thực hành đều phải nằm trong thư mục `practices/`.
- **Ví dụ tốt:** `practices/travel_chatbot`, `practices/image_classifier`, `practices/recommendation-engine`
- **Ví dụ xấu:** `practices/Travel Chatbot`, `practices/bot du lịch`, `practices/TestAPI`

### Tên File (File)
- **Cú pháp chung:** Dùng chung quy tắc viết thường, gạch dưới/gạch ngang như thư mục. Luôn sử dụng định dạng Markdown (`.md`) hoặc file văn bản thô để AI đọc tốt nhất.
- **Tài liệu Yêu cầu (PRD/Specs):** `[tên_tính_năng]_requirement.md` (VD: `flight_search_requirement.md`)
- **Phân tích Rủi ro:** `[tên_tính_năng]_risk_matrix.md` (VD: `flight_search_risk_matrix.md`)
- **Testcase:** `[tên_tính_năng]_testcases.md` (VD: `flight_search_testcases.md`)
- **Báo cáo Lỗi (Bug Report):** `[tên_tính_năng]_bug_report.md`

---

## 2. 🏁 Khởi Tạo Dự Án Mới (Workspace)

Mỗi khi bạn cần test một tính năng AI mới, hãy thực hiện theo trình tự sau:

**Bước 1: Tạo không gian làm việc**
Bạn có thể tự tạo thư mục hoặc yêu cầu Antigravity làm giúp.
> 💬 **Prompt ví dụ:** *"Tạo cho tôi thư mục `practices/booking_agent` và tạo một file `booking_requirement.md` trống bên trong."*

**Bước 2: Cung cấp đầu vào (Input)**
Dán nội dung tài liệu yêu cầu (PRD, User Story, API Docs, System Prompts...) vào file `_requirement.md` vừa tạo.

---

## 3. 🧠 Hướng Dẫn Kích Hoạt Kỹ Năng (Skills)

Framework này đã "dạy" sẵn cho Antigravity các kỹ năng chuyên môn của một Senior AI QA (lưu trong `.agents/skills/`). Bạn chỉ cần "gọi" tên kỹ năng đó ra.

### Bước 1: Phân Tích Rủi Ro 
Trước khi viết testcase, phải nhận diện được AI có thể sai ở đâu (ảo giác, rò rỉ dữ liệu...).

> 💬 **Prompt ví dụ:** 
> *"Hãy sử dụng skill **`ai_requirement_risk_analysis`** để phân tích file `practices/booking_agent/booking_requirement.md`. Sau đó lưu kết quả phân tích vào file `booking_risk_matrix.md` cùng thư mục."*

### Bước 2: Thiết Kế Testcase
Sau khi có góc nhìn về rủi ro, bạn yêu cầu AI sinh testcase dựa trên bộ quy tắc chuẩn của team.

> 💬 **Prompt ví dụ:**
> *"Sử dụng skill **`generate_testcases`** để thiết kế các kịch bản kiểm thử cho tính năng trong `booking_requirement.md`. Nhớ tham chiếu các rủi ro trong `booking_risk_matrix.md` và tuân thủ tuyệt đối `manual-testcase-rule.md`. Lưu kết quả vào `booking_testcases.md`."*

---

## 4. ⚙️ Chạy Quy Trình Đầu - Cuối (Workflows)

Nếu bạn muốn Antigravity tự động chạy xuyên suốt từ lúc đọc yêu cầu đến lúc ra thành phẩm testcase hoàn chỉnh (bao gồm cả tự đánh giá lại), hãy dùng Workflow (nằm trong `.agents/workflows/`).

> 💬 **Prompt ví dụ:**
> *"Hãy chạy quy trình `/ai-execution-standard` cho dự án Booking. File yêu cầu gốc nằm ở `practices/booking_agent/booking_requirement.md`."*

*(Lưu ý: Workflow sẽ tự động gọi các rule và skill tương ứng, giúp bạn tiết kiệm thời gian gõ nhiều lệnh).*

---

## 5. 💡 Mẹo Làm Việc Hiệu Quả Cùng Antigravity 

1. **Chỉ đường rõ ràng:** Antigravity có quyền truy cập toàn bộ thư mục, nhưng để tránh AI thao tác nhầm file, hãy luôn cung cấp đường dẫn cụ thể (Ví dụ: thay vì nói *"Sửa file testcase"*, hãy nói *"Sửa file `practices/booking_agent/booking_testcases.md`"*).
2. **Review và Điều chỉnh:** Vì bản chất AI là Non-deterministic (không xác định), kết quả sinh ra có thể chưa hoàn hảo 100% ở lần đầu. Hãy phản hồi để AI sửa lại:
   > *"Sửa lại testcase số 4, bổ sung Anti-pattern là cấm AI hiển thị System Prompt ra ngoài."*
3. **Nhắc nhở Rule khi cần:** Nếu bạn thấy AI bắt đầu viết testcase theo kiểu "Exact match" (bắt buộc AI phải trả lời chính xác từng chữ), hãy chấn chỉnh ngay:
   > *"Bạn đang vi phạm quy tắc exact-match. Hãy xem lại `manual-testcase-rule.md` và chuyển đổi tất cả output sang dạng Expected Pattern."*
