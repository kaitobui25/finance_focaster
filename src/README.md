# Nguồn Mã Core (src/) - Kiến trúc Clean Architecture

Thư mục `src/` chứa toàn bộ logic nghiệp vụ cốt lõi của ứng dụng Finance Forecaster. Dự án này được thiết kế theo tư tưởng **Clean Architecture (Architecture Domain-Driven Design)**, tách biệt hoàn toàn giữa:
- **Nghiệp vụ cốt lõi (Domain)**
- **Luồng xử lý dữ liệu (Use Cases)**
- **Công nghệ bên ngoài (Adapters / Infrastructure)**

Nguyên tắc tối thượng: **Dependency Rule**. Các module bên ngoài (giao diện, cơ sở dữ liệu, framework) phải phụ thuộc vào các module bên trong (nghiệp vụ). Module bên trong KHÔNG BAO GIỜ được biết hay import bất cứ thứ gì từ module bên ngoài.

---

## Cấu trúc chi tiết

### 1. `domain/` (Trung tâm vũ trụ)
Đây là lõi của hệ thống, chứa các khái niệm nghiệp vụ thuần túy. Nó không phụ thuộc vào BẤT KỲ framework, thư viện ngoại lai nào (trừ các thư viện chuẩn của Python như `dataclasses`, `datetime`).

* **`entities/`**: Khai báo các đối tượng dữ liệu như `Article`, `FeedSource`, `DailyReport`.
* **`interfaces/`**: Khai báo các **Abstract Base Classes (ABC)** như `ArticleRepository`, `FeedParser`. Đây là các "hợp đồng" mà các layer bên ngoài phải tuân thủ để giao tiếp với Domain.

*Quy tắc:* File trong `domain/` tuyệt đối không được `import` từ `adapters/`, `infrastructure/` hay `use_cases/`.

### 2. `use_cases/` (Nhạc trưởng điều phối)
Nơi chứa logic các chức năng chính của ứng dụng (Luồng quy trình). Trách nhiệm của các Use Case là lấy dữ liệu từ các Repository/Interface, thực hiện tính toán, điều phối và gọi các Interface khác để lưu trữ hoặc gửi đi.

* **`crawl_feeds.py`**: Lấy config RSS -> Gọi Parser lấy bài viết -> Lưu bài mới vào Repository.
* **`analyze_articles.py`**: Lấy bài chưa xử lý từ Repository -> Bắn qua LLM phân tích -> Cập nhật lại vào Repository.
* **`generate_report.py`**: Lấy bài đã phân tích trong ngày -> Đưa LLM tổng hợp báo cáo -> Gửi qua Notification Sender -> Lưu lịch sử vào Repository.

*Quy tắc:* Các Use Case chỉ nhận Dependency Injection (qua constructor) thông qua các Interface định nghĩa ở `domain/interfaces/`. Chúng không bao giờ biết mình đang gọi vào PostgreSQL, Gemini hay Telegram; chúng chỉ biết gọi hàm `save()`, `parse()`, `send()`.

### 3. `adapters/` (Người phiên dịch)
Nơi chứa các **Concrete Implementations** (Thực thi cụ thể) của các Interface được định nghĩa trong `domain/`. Adapter có nhiệm vụ làm cầu nối, dịch các khái niệm nghiệp vụ sang kỹ thuật thực tế và ngược lại.

* **`postgres_repository.py`**: Thực thi `ArticleRepository`, biến lời gọi `repo.save(article)` thành câu lệnh SQL `INSERT INTO articles...` chạy trên PostgreSQL (sử dụng thư viện `psycopg2`).
* **`rss_parser.py`**: Thực thi `FeedParser`, dùng thư viện `feedparser` thực tế để cào dữ liệu từ URL.
* **`gemini_client.py`**: Kết nối với SDK của Google GenAI thực tế.
* **`telegram_sender.py`**: Gửi tin nhắn thực tế qua API của Telegram.

*Quy tắc:* Được phép import từ `domain/` và các thư viện bên ngoài (pip). Không chứa business logic phức tạp, chỉ làm nhiệm vụ "chuyển đổi".

### 4. `infrastructure/` (Bệ phóng kỹ thuật)
Chứa các thành phần cấu hình nền tảng, thiết lập thư viện cốt lõi, và quan trọng nhất là "nối dây" (Wiring) cho toàn bộ ứng dụng.

* **`database.py`**: Quản lý Connection Pool, Context Manager của PostgreSQL.
* **`config.py`**: Đọc các cấu hình từ biến môi trường (`.env`).
* **`container.py`**: Dependency Injection (DI) Container. Nơi DUY NHẤT trong codebase biết tất cả mọi thứ. Nó thực hiện việc khởi tạo các Adapter cụ thể (`PostgresRepository`) và tiêm vào các `UseCase`.
* **`scheduler.py`**: Cấu hình `APScheduler` để hẹn giờ chạy các job định kỳ.
* **`logging_config.py`**: Định dạng format log output.

---

## Luồng hoạt động (Data Flow)

1. Root script (`main.py`) gọi `Container`.
2. `Container` đọc `Config`, khởi tạo PostgreSQL Connection, khởi tạo LLM Client, RSS Parser.
3. `Container` khởi tạo các Use Case (`CrawlFeedsUseCase`, `AnalyzeArticlesUseCase`...) và truyền các Adapter tương ứng vào.
4. Khi Use Case chạy, nó gọi các method trên Interface. Ở tầng thực thi, chính các Adapter trong `adapters/` sẽ hoạt động. Dữ liệu chạy từ Adapter -> Use Case (theo chuẩn Domain Entity) -> Adapter (để lưu xuống DB PostgreSQL).

Việc áp dụng kiến trúc này giúp project **Finance Forecaster** dễ dàng nâng cấp sau này (vd: đổi qua MySQL, đổi từ RSS sang API báo chí trả phí, hay chuyển từ Gemini sang GPT) mà không làm ảnh hưởng hay phải sửa đổi bất kỳ logic lõi nào trong `use_cases/` và `domain/`.
