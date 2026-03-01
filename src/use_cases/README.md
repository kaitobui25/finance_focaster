# Thư mục `use_cases/` (Bộ Não Điều Phối)

Trong kiến trúc Clean Architecture, `use_cases/` (hay còn gọi là Application Business Rules) chứa **quy trình nghiệp vụ tĩnh** của ứng dụng. Đây là nơi bạn trả lời câu hỏi: *"Hệ thống này thực sự làm những công việc gì?"*

Nếu bạn mở thư mục này ra, bạn sẽ thấy ngay 3 chức năng cốt lõi của **Finance Forecaster**:
1. Cào tin tức (`crawl_feeds.py`)
2. Phân tích tin tức bằng AI (`analyze_articles.py`)
3. Tổng hợp và gửi báo cáo (`generate_report.py`)

---

## Nguyên Tắc Hoạt Động

### Đặc quyền "Trưởng Phòng"
Các module trong `use_cases/` đóng vai trò như trưởng phòng điều phối:
- Nó không tự tay đi lấy móc dữ liệu từ DB (đó là việc của `adapters/`).
- Nó không tự tay phân tích ngôn ngữ (đó là việc của AI / `gemini_client`).
- Việc của nó là: **Nhận lệnh -> Gọi kho lấy đồ -> Gọi thợ xử lý -> Gọi kho cất đồ / Gọi shiper đi giao.**

### Tính "Mù Công Nghệ"
Các class trong `use_cases/` **TUYỆT ĐỐI KHÔNG BIẾT** bất kì công nghệ cụ thể nào.
- Nhìn vào code của Use Case, bạn sẽ không thấy dòng chữ `psycopg2`, `SQL`, `Gemini`, hay `Telegram` nào.
- Thay vào đó, nó giao tiếp qua các **Interfaces** (hợp đồng) được định nghĩa ở tầng `domain/` như `ArticleRepository`, `LLMClient`, `NotificationSender`.

*Ví dụ trong `CrawlFeedsUseCase`:*
Nó chỉ gọi `self.feed_parser.parse(source)`. Nó không quan tâm cái `feed_parser` đó dùng thư viện `feedparser` hay là dùng `BeautifulSoup`, miễn là nó trả về danh sách đối tượng `Article`.

---

## Danh Sách Các Băng Chuyền (Use Cases)

### 1. Băng chuyền cào tin: `CrawlFeedsUseCase`
- **Nhiệm vụ:** Đọc danh sách tạp chí từ file `feeds.yaml`, cho từng tạp chí đi lấy bài, kiểm tra xem bài đó đã có trong Database chưa, nếu chưa thì cất vào DB.
- **Biến phụ thuộc (Dependencies):** Cần một anh thợ cào tin (`FeedParser`) và một thủ kho (`ArticleRepository`).

### 2. Băng chuyền phân tích: `AnalyzeArticlesUseCase`
- **Nhiệm vụ:** Hỏi thủ kho xem dạo này có bài nào mới cào về mà chưa đọc không. Gom đống đó lại, gọi ông thần AI đọc từng bài, tóm tắt và gắn hashtag (TOPIX, BOJ...). Xong xuôi thì báo thủ kho update trạng thái.
- **Biến phụ thuộc (Dependencies):** Cần ông thần AI (`LLMClient`) và thủ kho (`ArticleRepository`).

### 3. Băng chuyền in báo cáo: `GenerateReportUseCase`
- **Nhiệm vụ:** Hỏi thủ kho xem hôm nay đã phân tích được những bài nào. Bưng nguyên đống đó đưa anh AI vắt óc viết thành bài nghị luận dài (Báo cáo tổng hợp). Sau đó, cất bản nháp vào kho lịch sử, và gọi anh bưu tá đem gửi cho sếp.
- **Biến phụ thuộc (Dependencies):** Cần 4 bên: AI viết lách (`LLMClient`), kho lưu bài báo (`ArticleRepository`), kho lưu report (`ReportRepository`), và bưu tá (`NotificationSender`).

---

## Lợi ích khổng lồ: Môi Trường Khép Kín (Testability)
Vì Use Case hoàn toàn mù dở về công nghệ bên ngoài, chúng ta có thể Unit Test chúng một cách hoàn hảo mà không cần Internet, không cần Database thật, không cần tài khoản Gemini thật.

Khi test `AnalyzeArticlesUseCase`, ta chỉ cần tạo ra một ông `LLMClient` giả (chỉ return lại chuỗi "Đã hiểu"), và một `ArticleRepository` giả (lưu data vào RAM thay vì ổ cứng). Bấm nút chạy và kết quả có ngay trong 0.01 giây!
