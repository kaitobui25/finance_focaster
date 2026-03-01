# Thư mục `domain/` (Trái Tim Hệ Thống)

Thư mục `domain/` là tầng trung tâm và quan trọng nhất trong Clean Architecture. Nó chứa **các khái niệm cốt lõi của doanh nghiệp** (Business Domain) và **các hợp đồng giao tiếp** (Interfaces).

**Nguyên tắc vàng:** File trong thư mục `domain/` **KHÔNG BAO GIỜ** được phép dùng lệnh `import` để gọi thư viện ngoại lai (như `requests`, `psycopg2`, `feedparser`, `gemini`). Nó chỉ được dùng các thư viện chuẩn của ngôn ngữ Python (như `dataclasses`, `datetime`, `abc`).

Nó hoàn toàn "mù" về việc nó đang chạy trên nền Web, Console, hay dùng Database gì.

---

## 1. `entities/` (Các thực thể kinh doanh)

Đây là nơi định nghĩa "dữ liệu" mà hệ thống của chúng ta quan tâm. Các `dataclass` này đại diện cho thế giới thực, không mang nặng logic kỹ thuật.

*   **`Article` (`article.py`)**: Đại diện cho một tin tức/bài báo tài chính độc lập.
    *   *Nội dung:* Chứa Tiêu đề, Link URL, Nội dung gốc, Bản tóm tắt của AI, Tags (Nikkei, TOPIX...), và trạng thái `is_processed` (Đã được LLM phân tích hay chưa?).
*   **`FeedSource` (`article.py`)**: Đại diện cho một "tờ báo" (VD: Japan Times Business).
    *   *Nội dung:* Tên, URL file định dạng XML (RSS), Ngôn ngữ và Thể loại tin.
*   **`DailyReport` (`article.py`)**: Bản báo cáo tổng hợp để gửi sếp.
    *   *Nội dung:* Định dạng Markdown dài (tóm tắt vĩ mô, cảnh báo Yên Nhật...), Ngày báo cáo và Loại báo cáo (Sáng/Chiều).

## 2. `interfaces/` (Hợp đồng lao động)

Đây là nơi định nghĩa các "bản hợp đồng" (Abstract Base Classes - ABC) cho các công cụ ngoại vi. Tầng Use Cases (`use_cases/`) sẽ dựa vào hợp đồng này để làm việc, còn tầng Adapters (`adapters/`) sẽ ký và thi hành hợp đồng này.

*   **`ArticleRepository` & `ReportRepository` (`repositories.py`)**
    *   *Hợp đồng:* Trả về interface để `save()` một Bài báo/Báo cáo, `find_unprocessed()` để lấy danh sách cần AI đọc, `mark_processed()` sau khi AI phân tích xong.
    *   *Lý do:* Tầng `use_cases/` cần lưu bài viết, nhưng nó không quan tâm bạn dùng file Excel, SQLite hay PostgreSQL, miễn là bạn có hàm `save(article)`. (Hiện tại được thi hành bởi `PostgresArticleRepository`).
*   **`FeedParser` (`repositories.py`)**
    *   *Hợp đồng:* Yêu cầu một hàm `parse(feed_source) -> list[Article]`. Lấy feed gõ đầu ra bài viết chuẩn `Article`.
    *   *Lý do:* Nguồn tin có thể đến qua RSS (`feedparser`), API Bloomberg (`requests`), hay cào HTML Selenium. Interface này giúp ứng dụng không bị trói buộc với một thư viện lấy link cụ thể.
*   **`LLMClient` (`repositories.py`)**
    *   *Hợp đồng:* Yêu cầu hàm `analyze_article` (trả tóm tắt + tags) và hàm `generate_report` (trả nguyên văn báo cáo).
    *   *Lý do:* Hệ thống cần "Não", nhưng cái não này nay có thể là Google Gemini, mai có thể là OpenAI ChatGPT, thậm chí là Llama Cloud API. Viết code Interface tốt giúp thay vỏ não trong 10 phút.
*   **`NotificationSender` (`repositories.py`)**
    *   *Hợp đồng:* Yêu cầu hàm `send(message)`.
    *   *Lý do:* Nay báo cáo gửi qua `văn bản Console`, mai gửi qua `Bot Telegram`, mốt gửi qua `Gmail` – Use Case của ta chỉ gọi mỗi hàm `.send()`.

---

## Tóm lại
`domain/` định nghĩa luật chơi ("Tôi cần một thứ lấy được tin bài dưới dạng object Article"). `adapters/` là những người tới tham gia trò chơi ("Tôi cung cấp tính năng đó bằng code thư viện psycopg2 / gemini"). Tầng `use_cases/` ở giữa điều phối luồng trò chơi này.
