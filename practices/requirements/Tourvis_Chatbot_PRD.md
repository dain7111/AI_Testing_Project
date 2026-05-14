# Tourvis AI Chatbot - Product Requirements Document (PRD)

## 1. Overview
**Mục tiêu:**
Xây dựng một AI chatbot cho nền tảng du lịch Tourvis nhằm tự động hóa quá trình hỗ trợ khách hàng, cải thiện trải nghiệm người dùng và giảm tải cho bộ phận Customer Service (CS). Chatbot sẽ đóng vai trò là trợ lý ảo, chuyên giải đáp các thắc mắc thường gặp liên quan đến sản phẩm, dịch vụ, đặt chỗ, thanh toán và các chính sách của Tourvis.

**Đối tượng người dùng:**
Khách hàng truy cập website/app Tourvis đang tìm kiếm thông tin, có nhu cầu đặt dịch vụ hoặc cần hỗ trợ sau khi đặt dịch vụ.

**Phạm vi (Scope):**
- **In-scope (Hỗ trợ chính):** 
  - Thông tin sản phẩm: Hàng không, hotel, tour & tickets do Tourvis cung cấp.
  - Liên quan đến đặt chỗ: Hướng dẫn cách đặt chỗ, xác nhận đặt chỗ, thay đổi đặt chỗ.
  - Liên quan đến thanh toán: Hướng dẫn về phương tiện thanh toán, lỗi thanh toán, ưu đãi trả góp không lãi.
  - Hủy và hoàn tiền: Hướng dẫn thủ tục hủy sản phẩm, quy định hoàn tiền.
  - Ưu đãi và khuyến mãi: Thông tin ưu đãi như giảm giá, sự kiện diễn ra tại Tourvis.
  - Các dịch vụ khác: Voucher, cấp hóa đơn, đăng ký bảo hiểm cho khách du lịch.
- **Out-of-scope (Không hỗ trợ):** 
  - Quy định cụ thể của từng hãng hàng không.
  - Các thắc mắc liên quan đến PRIVIA.

---

## 2. Strategic View

### 2.1. Jobs-to-be-Done (JTBD)
- **Khi** tôi gặp vấn đề trong quá trình đặt vé/phòng trên Tourvis, **tôi muốn** nhận được sự hỗ trợ và hướng dẫn tức thì, **để** tôi có thể hoàn thành giao dịch mà không bị gián đoạn.
- **Khi** tôi muốn thay đổi hoặc hủy dịch vụ, **tôi muốn** biết rõ quy trình và chính sách hoàn tiền, **để** tôi có thể đưa ra quyết định phù hợp và tránh mất phí oan.
- **Khi** tôi gặp lỗi thanh toán, **tôi muốn** biết nguyên nhân và cách khắc phục hoặc các ưu đãi trả góp, **để** tôi có thể thanh toán thành công.

### 2.2. SWOT Analysis
| Yếu tố | Chi tiết |
|---|---|
| **Strengths** (Điểm mạnh) | Giảm thời gian chờ đợi của khách hàng, phản hồi tức thời 24/7. Giải đáp chính xác các chính sách sẵn có của Tourvis. |
| **Weaknesses** (Điểm yếu) | Không thể xử lý các case phức tạp vượt ngoài kịch bản; phụ thuộc vào dữ liệu đầu vào. |
| **Opportunities** (Cơ hội) | Ứng dụng AI/NLP giúp hiểu intent người dùng tốt hơn, tăng tỷ lệ chuyển đổi từ các chương trình khuyến mãi. |
| **Threats** (Thách thức) | Cung cấp sai thông tin chính sách có thể dẫn đến khiếu nại; người dùng thất vọng nếu bot liên tục trả lời sai hoặc không hiểu ý. |

---

## 3. Success Metrics (KPIs)
- **Tỷ lệ giải quyết thành công (Deflection Rate):** > 60% các câu hỏi được xử lý thành công bởi chatbot mà không cần chuyển cho nhân viên CS.
- **CSAT (Customer Satisfaction Score):** > 4.0/5.0 cho các phiên tương tác với chatbot.
- **Thời gian phản hồi (Response Time):** Dưới 3 giây cho mỗi câu hỏi.
- **Tỷ lệ Fallback:** < 15% (Số lần bot không hiểu ý người dùng và phải yêu cầu nhập lại).

---

## 4. User Stories & Acceptance Criteria

### US01: Tra cứu thông tin sản phẩm
**As a** khách hàng, **I want to** hỏi thông tin về các sản phẩm (hàng không, chỗ ở, tour, vé) **so that** tôi biết Tourvis đang cung cấp những dịch vụ gì.
- **Acceptance Criteria:**
  - Bot có khả năng liệt kê và mô tả ngắn gọn các loại sản phẩm của Tourvis.
  - Bot cung cấp link dẫn đến trang tìm kiếm hoặc chi tiết sản phẩm liên quan.

### US02: Hướng dẫn & Hỗ trợ đặt chỗ
**As a** khách hàng, **I want to** nhận được hướng dẫn về cách đặt chỗ, xác nhận và thay đổi đặt chỗ **so that** tôi có thể tự thao tác trên hệ thống.
- **Acceptance Criteria:**
  - Bot cung cấp hướng dẫn từng bước (step-by-step) cách thao tác đặt chỗ.
  - Bot hướng dẫn cách truy cập vào trang quản lý đơn hàng để xác nhận hoặc thay đổi thông tin đặt chỗ.

### US03: Hỗ trợ thanh toán
**As a** khách hàng, **I want to** hỏi về phương thức thanh toán, lỗi thanh toán và ưu đãi trả góp **so that** tôi có thể thanh toán thành công.
- **Acceptance Criteria:**
  - Bot liệt kê các phương thức thanh toán được hệ thống Tourvis chấp nhận.
  - Bot cung cấp hướng dẫn khắc phục các lỗi thanh toán phổ biến.
  - Bot thông tin chi tiết về các đối tác có ưu đãi trả góp 0%.

### US04: Chính sách Hủy & Hoàn tiền
**As a** khách hàng, **I want to** biết thủ tục hủy và chính sách hoàn tiền của Tourvis **so that** tôi thực hiện đúng quy trình.
- **Acceptance Criteria:**
  - Bot cung cấp quy trình và các bước yêu cầu hủy dịch vụ.
  - Bot giải thích các quy định chung về phí hủy và thời gian dự kiến nhận lại tiền hoàn.

### US05: Ưu đãi & Dịch vụ khác
**As a** khách hàng, **I want to** biết về các khuyến mãi hiện có, cách sử dụng voucher, xuất hóa đơn và mua bảo hiểm **so that** tôi tối ưu được chi phí và được bảo vệ.
- **Acceptance Criteria:**
  - Bot cung cấp thông tin/link về các sự kiện giảm giá đang diễn ra.
  - Bot hướng dẫn chi tiết cách nhập voucher, các bước xuất hóa đơn và cách mua bảo hiểm du lịch.

### US06: Xử lý các câu hỏi Out-of-Scope (Hãng bay & PRIVIA)
**As a** khách hàng, **I want to** hỏi về quy định của hãng bay cụ thể hoặc dịch vụ PRIVIA, **so that** tôi có thông tin đầy đủ cho chuyến đi.
- **Acceptance Criteria:**
  - Bot nhận diện được các từ khóa liên quan đến "quy định hãng hàng không" hoặc "PRIVIA".
  - Bot phản hồi từ chối lịch sự, nêu rõ giới hạn hỗ trợ.
  - Bot cung cấp cách liên hệ đúng (VD: hotline hãng bay, website hãng hoặc hotline PRIVIA) thay vì trả lời sai.

---

## 5. Business Rules (Quy tắc nghiệp vụ)

Các quy tắc kinh doanh dưới đây định nghĩa cách hệ thống Chatbot phản hồi dựa trên từng điều kiện cụ thể (IF-THEN):

| Condition (Điều kiện - IF) | Action (Hành động - THEN) | Error/Message (Thông báo) |
|---|---|---|
| **Intent:** Hỏi về quy định của hãng hàng không (hành lý, check-in, delay, quy định đặc biệt...) | Chuyển hướng người dùng sang kênh CSKH của hãng bay tương ứng hoặc khuyên liên hệ trực tiếp hãng. | "Xin lỗi, Tourvis không thể hỗ trợ trực tiếp các quy định cụ thể của hãng hàng không. Vui lòng liên hệ hotline của hãng hoặc xem trên website của hãng để biết thông tin chính xác nhất." |
| **Intent:** Hỏi về dịch vụ hoặc thắc mắc liên quan đến PRIVIA | Từ chối hỗ trợ và cung cấp thông tin liên hệ của bộ phận PRIVIA. | "Xin lỗi, hiện tại tôi không thể giải đáp các thắc mắc liên quan đến PRIVIA. Bạn vui lòng liên hệ [Hotline/Link PRIVIA] để được hỗ trợ chi tiết." |
| **Intent:** Hỏi thông tin về thủ tục hoàn/hủy | Cung cấp chính sách chung của Tourvis và link dẫn đến trang Quản lý đơn hàng của user. | "Để xem chi tiết quy định hoàn/hủy cho đơn hàng của bạn, vui lòng truy cập [Link quản lý đơn hàng]. Theo quy định chung của Tourvis..." |
| **Intent:** Gặp lỗi thanh toán / Hỏi về trả góp | Cung cấp thông tin trả góp, các bước kiểm tra khi lỗi thanh toán. | "Nếu bạn gặp lỗi thanh toán, vui lòng kiểm tra lại hạn mức thẻ hoặc kết nối mạng. Tourvis hiện hỗ trợ trả góp 0% qua các ngân hàng [Danh sách ngân hàng]..." |
| **Intent:** Không xác định (Fallback) hoặc tự tin thấp | Yêu cầu người dùng cung cấp thêm thông tin hoặc diễn đạt lại câu hỏi. | "Xin lỗi, tôi chưa hiểu rõ ý của bạn. Bạn có thể nói rõ hơn về dịch vụ bạn đang quan tâm (ví dụ: vé máy bay, khách sạn, thanh toán, hoàn/hủy...) được không?" |

---

## 6. Non-Functional Requirements
- **Performance:** Thời gian xử lý NLP và phản hồi phải dưới 3 giây.
- **Availability:** Chatbot phải luôn sẵn sàng 24/7 với Uptime đạt 99.9%.
- **Security & Data Privacy:** Không hiển thị, không lưu trữ (hoặc phải mã hóa) thông tin cá nhân nhạy cảm (PII, số thẻ tín dụng) của khách hàng trong logs hệ thống.
- **Language Processing:** Hỗ trợ ngôn ngữ Tiếng Việt tự nhiên, có khả năng xử lý lỗi sai chính tả nhẹ, không dấu và viết tắt phổ biến trong lĩnh vực du lịch.
