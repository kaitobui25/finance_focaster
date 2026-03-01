# Thư mục `infrastructure/` (Bộ Khung & Hệ Thống Động Cơ)

Nếu `domain/` là trái tim và `use_cases/` là não bộ, thì `infrastructure/` chính là hệ thống điện, đường ống nước, và khung gầm của toàn bộ dự án Finance Forecaster. 

Đúng như tên gọi (cơ sở hạ tầng), tầng này giải quyết tất cả các bài toán **kỹ thuật thuần túy** để đảm bảo ứng dụng có thể chạy được trên một máy chủ thực tế.

---

## Danh sách các chức năng chính

### 1. Quản lý trạng thái Khởi động (Setup)
*   **`config.py`**: Điểm thu thập cấu hình duy nhất. Nó đọc các biến môi trường từ file `.env` (như `GEMINI_API_KEY`, `DATABASE_URL`), kiểm tra tính hợp lệ của chúng, và đóng gói thành một đối tượng `AppConfig` an toàn. Bất kỳ rò rỉ secret nào cũng sẽ bị chặn lại ở đây.
*   **`logging_config.py`**: Thiết lập định dạng log chuẩn (Thời gian, Tên module, Cấp độ báo lỗi) cho toàn bộ ứng dụng. Phải khởi chạy cái này đầu tiên trước khi hệ thống kịp phun ra bất kỳ dòng text nào.

### 2. Quản lý Tài nguyên Dài hạn (Persistent Resources)
*   **`database.py`**: Quản lý Pool kết nối tới PostgreSQL (nhờ thư viện `psycopg2`). Nó cung cấp một *Context Manager* (`with db.connect() as conn:`) để đảm bảo Mọi Kết Nối Đều Được Đóng lại an toàn (chống rò rỉ bộ nhớ), và tự động `commit()` hoặc `rollback()` khi có lỗi.
*   **`scheduler.py`**: Cấu hình bộ máy tự động hóa `apscheduler`. Định nghĩa mấy giờ báo cáo sáng chạy (07:45), mấy giờ báo cáo chiều chạy (16:30), và bao lâu thì đi crawl RSS một lần (cách nhau 2 tiếng).

### 3. "Dây thần kinh" kết nối - `container.py` (Dependency Injection - DI)
Đây là file **SIÊU QUAN TRỌNG**, là **trung tâm duy nhất trên toàn cõi project** biết tất cả mọi thứ kết nối với nhau ra sao.

*   *Bài toán:* `CrawlFeedsUseCase` cần một cái `FeedParser` và một cái `ArticleRepository` để chạy. Bản thân Use Case không được phép biết file `rss_parser` nằm ở đâu vì vi phạm triết lý Clean Architecture.
*   *Cách Container giải quyết:* 
    1. Khởi tạo `Khung Cầm Tay`: `parser = FeedparserRSSParser()`
    2. Khởi tạo `Nhà Kho`: `repo = PostgresArticleRepository(database)`
    3. Tiêm chúng vào `UseCase`: `return CrawlFeedsUseCase(feed_parser=parser, article_repo=repo)`

Cách thiết kế này giúp Unit Test cực kỳ sung sướng. Khi test `CrawlFeedsUseCase`, thay vì dùng `PostgresArticleRepository` thật (chạm vào DB thật làm chậm máy), ta chỉ cần "tiêm" một `MockRepository` (nhà kho giả) vào là test chạy nhanh như chớp.

---

## Ranh giới nghiêm ngặt
File `main.py` ở ngoài cùng dự án chỉ biết và gọi đúng 1 thứ: **Container**. `main.py` không bao giờ gọi hay import thẳng `PostgresRepository` hay `GeminiClient`. Nó chỉ nói với `Container`: "Ê, lấy cho tao bản Use Case đi cào bài viết cái!". `Container` sẽ lo đắp nối mọi thứ thành 1 khối hoàn chỉnh và quăng lại cho `main.py` nhấn nút Start.
