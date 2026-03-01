# Hướng dẫn Deploy Finance Forecaster lên VPS (Ubuntu/Debian)

Tài liệu này hướng dẫn cách deploy ứng dụng Finance Forecaster lên một VPS sử dụng Docker và Docker Compose. GitHub Actions đã đảm nhận việc test và đóng gói ứng dụng thành Docker Image.

## Yêu cầu chuẩn bị
1. **Một VPS** chạy Ubuntu (20.04 hoặc 22.04 LTS) hoặc Debian.
2. VPS đã được mở port **5432** (nếu cần truy cập DB từ bên ngoài) dù khuyên dùng tường lửa mặc định và chỉ cho phép internal network của Docker.
3. Đã cài đặt **Docker** và **Docker Compose** trên VPS.
4. Đã có **Telegram Bot Token**, **Chat ID** và **Gemini API Key**.

---

## Bước 1: Chuẩn bị VPS
SSH vào VPS của bạn:
```bash
ssh user@your_vps_ip
```

Tạo một thư mục cho dự án:
```bash
mkdir -p ~/finance_forecaster
cd ~/finance_forecaster
```

## Bước 2: Chuẩn bị file cấu hình
Bạn chỉ cần 3 file trên VPS để khởi chạy (không cần mang toàn bộ source code lên):
1. `docker-compose.yml`
2. `.env`
3. `db/init.sql`

**Lấy file `docker-compose.yml` và thư mục `db` từ repo:**
```bash
wget https://raw.githubusercontent.com/Kaitobui/finance_forecaster/main/docker-compose.yml
mkdir -p db
wget -O db/init.sql https://raw.githubusercontent.com/Kaitobui/finance_forecaster/main/db/init.sql
```

**Tạo file `.env` chứa Secret Keys:**
```bash
nano .env
```
Copy nội dung sau vào và điền thông tin thật của bạn:
```env
# Mật khẩu DB (thay đổi thành mật khẩu an toàn)
POSTGRES_PASSWORD=your_secure_db_password

# Gemini & Telegram Secrets
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Config
CRAWL_INTERVAL_HOURS=2
MORNING_REPORT_TIME=07:45
EVENING_REPORT_TIME=16:30
TIMEZONE=Asia/Tokyo
LOG_LEVEL=INFO
```

## Bước 3: Khởi chạy Ứng dụng
Kéo image mới nhất (nếu cấu hình download image từ container registry như GitHub Packages / Docker Hub) hoặc cho Docker Compose tự động build lại ứng dụng (do `docker-compose.yml` có cấu hình `build: .` — yêu cầu có source code).

**Lưu ý:** Vì trong file `docker-compose.yml` hiện tại đang để `build: .`, nên cần clone toàn bộ repo dể chạy bằng tay nếu bạn không dùng Docker container registry (như Docker Hub):

```bash
# Clone source code
git clone https://github.com/Kaitobui/finance_forecaster.git .

# Tạo file .env như Bước 2 ở trên
nano .env 

# Chạy Docker Compose dưới nền
docker-compose up -d --build
```

## Bước 4: Kiểm tra trạng thái
Kiểm tra xem các containers đã chạy thành công chưa:
```bash
docker-compose ps
```
Hiển thị log của ứng dụng xem có lỗi gì không:
```bash
docker-compose logs -f app
```

## Cách Update Ứng dụng sau này
Mỗi lần code mới được đưa lên `main`, GitHub Actions sẽ chạy test. Khi test pass, để đưa phiên bản mới lên VPS, bạn chỉ cần gõ:
```bash
cd ~/finance_forecaster
git pull origin main
docker-compose up -d --build app
```
*(Việc này không ảnh hưởng đến dữ liệu Database vì Database đã được lưu vào Docker volume `pgdata`)*.
