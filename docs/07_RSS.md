Tuy Google đã gỡ bỏ giao diện hiển thị, nhưng "cổng kết nối ngầm" để xuất dữ liệu RSS của họ vẫn đang hoạt động tốt. Đường link tôi cung cấp cho bạn không phải lấy từ một nút bấm, mà là do tôi **tự ghép thủ công** dựa trên cú pháp ẩn của Google.

Dưới đây là cách "giải phẫu" công thức đó để bạn có thể tự tạo RSS cho bất kỳ trang web hoặc chủ đề nào mình muốn:

### Công thức bí mật tạo RSS từ Google News

Đường link RSS luôn được ghép lại từ 3 thành phần chính:

**1. Cấu trúc gốc (Bắt buộc):**

> `https://news.google.com/rss/search?q=`
> Đây là câu lệnh báo cho máy chủ Google biết: "Tôi muốn tìm kiếm và nhận kết quả dưới dạng chuỗi RSS".

**2. Từ khóa tìm kiếm:**
Bạn sẽ dán từ khóa hoặc lệnh tìm kiếm ngay sau dấu `=`.
Với Reuters, tôi đã sử dụng một toán tử tìm kiếm nâng cao của Google là `site:` để ép hệ thống chỉ quét đúng thư mục bạn cần:

> `site:reuters.com/business`

**3. Đuôi cài đặt ngôn ngữ và vị trí (Khuyên dùng):**
Để tránh việc Google News trả về kết quả bị lẫn lộn ngôn ngữ, chúng ta cần gắn thêm đoạn mã chỉ định. Với tin tức của Mỹ bằng tiếng Anh, đoạn mã sẽ là:

> `&hl=en-US&gl=US&ceid=US:en`

Khi bạn ghép sát 3 thành phần này lại với nhau (không để lại khoảng trắng nào), bạn sẽ có được đường link RSS hoàn hảo:
`https://news.google.com/rss/search?q=site:reuters.com/business&hl=en-US&gl=US&ceid=US:en`

---

### Cách ứng dụng cho các chủ đề khác

Bạn có thể tận dụng công thức này để gom tin tức cực kỳ hiệu quả.

**Ví dụ:** Nếu bạn muốn tạo một luồng RSS chỉ tập trung vào tin tức về "Trí tuệ nhân tạo" từ các báo **Việt Nam**, bạn chỉ cần thay từ khóa (nhớ thay khoảng trắng bằng dấu `+`) và đổi đuôi ngôn ngữ thành của Việt Nam (`&hl=vi&gl=VN&ceid=VN:vi`):

> `https://news.google.com/rss/search?q=Trí+tuệ+nhân+tạo&hl=vi&gl=VN&ceid=VN:vi`

Bạn có đang muốn theo dõi thêm một trang tin tức khó nhằn nào khác hay một chủ đề cụ thể nào không? Hãy nói tên trang đó, tôi sẽ ghép sẵn đường link RSS chuẩn xác giúp bạn nhé!
