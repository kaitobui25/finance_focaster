# Thư mục `adapters/` (Người Giao Tiếp)

Trong kiến trúc Clean Architecture, thư mục `adapters/` đóng vai trò là "Các tay lính đánh thuê" biên dịch giữa thế giới thực tiễn (Cơ sở dữ liệu, API bên thứ 3) với Core Nghiệp vụ (Use Cases & Entities).

Nguyên tắc bắt buộc: Các Adapter **phải Implement các Interface (ABC)** định nghĩa trong `src/domain/interfaces/`. Điều này giúp các service lõi (`use_cases/`) có thể dùng chúng một cách độc lập mà không cần biết chúng hoạt động bằng công nghệ gì.

---

## Danh sách các Adapter & Nhiệm vụ

### 1. `postgres_repository.py`
* **Implement Interface:** `ArticleRepository`, `ReportRepository`
* **Khách hàng phục vụ:** PostgeSQL (qua thư viện `psycopg2`).
* **Nhiệm vụ:** Convert các Entities Python (như `Article`) thành câu lệnh SQL (`INSERT`, `UPDATE`, `SELECT`) để lưu vào PostgreSQL. Trả dữ liệu từ CSDL về lại dưới định dạng thuần `Entity`.
* *Lưu ý:* Ban đầu dự án chạy bằng `sqlite_repository.py`, nhưng đã chốt chuyển hẳn qua PostgreSQL 100% để scale-up. Adapter SQLite cũ đã bị xóa.

### 2. `rss_parser.py`
* **Implement Interface:** `FeedParser`
* **Khách hàng phục vụ:** Các nguồn tin tức trên mạng (Japan Times, Nikkei) qua thư viện `feedparser` và `httpx`.
* **Nhiệm vụ:** Nhận một URL từ Job cấu hình. Dùng hàm HTTP get -> pass rác HTML vớt metadata -> Bóc tách (`title`, `link`, đoạn trích lược HTML `content`, `published_at`) thành đối tượng `Article` sạch đẹp.

### 3. `gemini_client.py`
* **Implement Interface:** `LLMClient`
* **Khách hàng phục vụ:** Google Gemini API 2.5 Flash qua bộ Open API client `google-genai`.
* **Nhiệm vụ:**
   1. Đọc nội dung bài báo, tóm tắt và bóc tách các tag quan trọng như (Nikkei, TOPIX, USD/JPY, BOJ...).
   2. Viết Báo Cáo chuyên sâu: Nhận input là hàng chục bài đã xử lý ở B1, nhào nặn theo System Prompt phong cách "Giám đốc Phân Tích Tài Chính Nhật Bản" và xuất ra báo cáo bằng markdown.

### 4. `telegram_sender.py`
* **Implement Interface:** `NotificationSender`
* **Khách hàng phục vụ:** Bot Telegram (giao thức HTTP đến server của Telegram) và Terminal màn hình Console.
* **Nhiệm vụ:** Chờ khi báo cáo Markdown được tạo xong ở `gemini_client` -> Push trực tiếp Report này qua tài khoản cá nhân/Group Telegram của bạn. Có 2 bản thực thi ở đây:
   - `TelegramNotificationSender`: Gắn API Key & Chat ID ném thẳng báo cáo.
   - `ConsoleNotificationSender`: (Fallback Mode) In báo cáo ra màn hình nếu chưa gắn khóa bí mật.

---

## Lợi ích khi cô lập API tồi vào Interface
- Nếu bạn hết gói free của Google **Gemini**, ta chỉ cần viết thêm `openai_client.py` và sửa `container.py`, code ruột của hệ thống không cần thay đổi dù chỉ 1 chữ.
- Nếu sau này không dùng Postgres mà chuyển qua Mongo, chỉ cần viết file `mongo_repository.py`.
