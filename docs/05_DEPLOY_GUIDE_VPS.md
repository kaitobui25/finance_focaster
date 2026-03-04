# Hướng dẫn Deploy Finance Forecaster lên VPS (Ubuntu/Debian)

Tài liệu hướng dẫn cách triển khai ứng dụng KAI-FINA lên VPS. Toàn bộ quá trình build image hiện đã được tự động hóa qua GitHub Actions và đẩy lên Docker Hub (`kaitobui/finance_forecaster:latest`).

## Yêu cầu chuẩn bị
1. **VPS** chạy Ubuntu (20.04/22.04 LTS) hoặc Debian.
2. VPS đã cài đặt sẵn **Docker** và **Docker Compose**.
3. Các khóa bí mật: **Telegram Bot Token**, **Chat ID** và **Gemini API Key**.

---

## Bước 1: Khởi tạo VPS & Cài đặt môi trường 
*(Bỏ qua nếu VPS của bạn đã có sẵn Docker và đủ RAM)*

SSH vào VPS của bạn và chạy đoạn mã thiết lập (Cài Docker + Tạo 2GB Swap RAM để chống sập máy):
```bash
sudo apt update && sudo apt install docker.io docker-compose git curl wget -y
sudo systemctl enable docker && sudo systemctl start docker
sudo usermod -aG docker $USER
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Tạo thư mục làm việc tĩnh:
```bash
mkdir -p ~/finance_forecaster
cd ~/finance_forecaster
```

---

## Bước 2: Tải Cấu hình Khởi chạy
Để deploy, bạn **không cần rồi toàn bộ source code**. Chỉ cần ba cấu hình cốt lõi: File Compose, Script DB, và biến môi trường.

**1. Tải `docker-compose.yml` và `init.sql`**
```bash
mkdir -p docker db
wget -O docker/docker-compose.yml https://raw.githubusercontent.com/kaitobui25/finance_focaster/main/docker/docker-compose.yml
wget -O db/init.sql https://raw.githubusercontent.com/kaitobui25/finance_focaster/main/db/init.sql
```

**2. Khởi tạo file biến môi trường (`.env`)**
```bash
nano .env
```
📋 Dán nội dung sau vào (nhớ thay các giá trị `xxxxxxxx` bằng key thực tế của bạn):
```env
POSTGRES_PASSWORD=StrongPassword123!

GEMINI_API_KEY=xxxxxxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=xxxxxxxxxxxxxxxx
TELEGRAM_CHAT_ID=xxxxxxxx

CRAWL_INTERVAL_HOURS=2
MORNING_REPORT_TIME=07:45
EVENING_REPORT_TIME=16:30
TIMEZONE=Asia/Tokyo
LOG_LEVEL=INFO

```
*(Lưu file: `Ctrl+O` -> `Enter`, Thoát: `Ctrl+X`)*

---

## Bước 3: Khởi chạy Ứng dụng
Hệ thống sẽ tự động tải image mới nhất từ Docker Hub về và cấu hình database.

```bash
docker-compose -f docker/docker-compose.yml up -d
```

**Kiểm tra trạng thái:**
- Xem danh sách container đang chạy:
```bash
  docker-compose -f docker/docker-compose.yml ps
```
- Xem log hoạt động để chắc chắn mọi thứ ổn:
 ```bash
  docker-compose -f docker/docker-compose.yml logs -f app
```

---

## Cách Update Ứng dụng (Sau này)
Bạn thiết lập CI/CD trên Github, nên mỗi khi push lên nhánh `main`, hệ thống tự build Docker Image mới. Khi muốn cập nhật code mới lên Server, bạn chỉ cần chạy:

```bash
cd ~/finance_forecaster
# Tải image phiên bản mới nhất từ Docker Hub
docker-compose -f docker/docker-compose.yml pull app
# Khởi động lại ứng dụng
docker-compose -f docker/docker-compose.yml up -d app
```

*(Lưu ý: Dữ liệu CSDL hoàn toàn an toàn do đã được ánh xạ vào volume độc lập `pgdata` của Docker).*
