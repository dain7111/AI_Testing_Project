# Ý tưởng tham khảo: AI Travel Chatbot - Requirements

## 1. Overview

Hệ thống là một AI chatbot tích hợp trên website/app du lịch (tương tự Booking.com, Expedia, Traveloka).

**Mục tiêu:**
- Trả lời câu hỏi người dùng về vé máy bay.
- Trả lời thông tin về khách sạn.
- Tư vấn chính sách (hoàn/hủy).
- Hỗ trợ tìm kiếm và gợi ý sản phẩm.
- Giảm tải cho CS (Customer Service) team.

---

## 2. Supported Features

### 2.1 Flight Inquiry (Hỏi về vé máy bay)
**Chatbot phải trả lời thông tin chuyến bay theo input:**
- Các thông tin cơ bản về vé máy bay
- Các thông tin về khách sạn
- Các thông tin về chính sách (hoàn/hủy)
- Các thông tin về tìm kiếm và gợi ý sản phẩm

**Ví dụ:**
> "Tôi muốn bay từ Hà Nội vào Đà Nẵng ngày mai"

**Expected:** 
Hiển thị các bước hướng dẫn người dùng tìm kiếm chuyến bay.

### 2.2 Hotel Search (Tìm khách sạn)
**Chatbot phải gợi ý khách sạn dựa trên:**
- Các thông tin cơ bản về khách sạn
- Các thông tin về chính sách (hoàn/hủy)
- Các thông tin về tìm kiếm và gợi ý sản phẩm

**Ví dụ:**
> "Tìm khách sạn ở Đà Lạt giá dưới 1 triệu"

**Expected:** 
Hiển thị các bước hướng dẫn người dùng tìm kiếm khách sạn.

### 2.3 Booking Policy Q&A
**Chatbot phải trả lời các câu hỏi dạng:**
- “Có hoàn vé không?”
- “Khách sạn này có free cancellation không?”

**Expected:**
- Trả lời đúng theo policy từ hệ thống backend.
- Nếu không chắc chắn → phải nói rõ (Yêu cầu: Không được sinh ra ảo giác - hallucinate).

### 2.4 Multi-turn Conversation
**Chatbot phải:** 
- Nhớ context (ngữ cảnh) trong cùng một session.

**Ví dụ:**
> **User:** “Tìm khách sạn ở Đà Lạt”
> **User:** “Giá dưới 1 triệu”

**Expected:** 
- Chatbot hiểu câu thứ 2 là điều kiện lọc liên quan trực tiếp đến câu thứ 1.

### 2.5 Fallback Handling
**Khi Bot không hiểu (Fallback):**
- Trả lời với cấu trúc: Xin lỗi + gợi ý user nhập lại.
- Hoặc đưa ra các suggestion thay thế để người dùng chọn.

### 2.6 Language Support
**Hỗ trợ đa ngôn ngữ:**
- Tiếng Việt
- Tiếng Anh

---

## 3. Input Requirements

### 3.1 Natural Language Input
**Hỗ trợ xử lý ngôn ngữ tự nhiên:**
- Typo nhẹ (Sai chính tả)
- Viết tắt
- Mixed language (Trộn VN + EN)

**Ví dụ:**
> “HN to DN tmr” (Hà Nội to Đà Nẵng tomorrow)
> “ks Đà Lạt rẻ” (Khách sạn Đà Lạt rẻ)

### 3.2 Invalid Input Handling
**Nếu input của người dùng:**
- Thiếu thông tin
- Không rõ intent (ý định)

**Expected:** 
- Chatbot tự động hỏi lại để làm rõ (clarification).

---

## 4. Output Requirements

### 4.1 Response Format
**Không được:**
- Trả lời quá dài (> 500 words).
- Trả lời quá ngắn (thiếu thông tin quan trọng).

**Bắt buộc:**
- Câu trả lời phải Clear (Rõ ràng).
- Format theo cấu trúc Structured (Sử dụng bullet/list nếu cần liệt kê).

### 4.2 Accuracy
- Thông tin giá vé, giờ bay phải **Match 100%** với backend API.

### 4.3 Tone
- Thái độ thân thiện (Friendly).
- Không quá suồng sã (casual).
- Tuyệt đối không dùng từ ngữ xúc phạm/phản cảm (offensive).

---

## 5. Performance
- **Response time:** < 3s cho các luồng query bình thường.
- **Timeout Handling:** Nếu xử lý > 5s → Phải hiển thị hiệu ứng UX loading + fallback message.

---

## 6. Error Handling

### 6.1 API Failure
- Nếu backend fail, hệ thống phản hồi hiển thị:
> “Hiện tại hệ thống đang bận, vui lòng thử lại sau…”

### 6.2 No Result
- Nếu không tìm kiếm có kết quả, trả lời:
> “Không tìm thấy kết quả phù hợp”
- Đồng thời đưa ra gợi ý thay đổi điều kiện tìm kiếm.

---

## 7. Security & Safety

**Cơ chế từ chối trả lời (Guardrails):**
- Từ chối các nội dung nhạy cảm.
- Từ chối các nội dung không liên quan đến du lịch (Out of Scope).

**Bảo mật dữ liệu:**
- Tuyệt đối không leak (rò rỉ) thông tin cá nhân của user khác.

---

## 8. Logging & Tracking
**Hệ thống phải Tracking các thông tin sau:**
- Cập nhật User input.
- Bot response.
- Error log.