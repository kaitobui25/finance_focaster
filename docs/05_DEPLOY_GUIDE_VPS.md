# 🚀 QUY TRÌNH CHUẨN DEPLOY VPS + DOCKER + SWAP 2GB

---

# PHẦN 1 — Chuẩn bị VPS

## 1️⃣ SSH vào VPS

```bash
ssh ubuntu@your_server_ip
```

Tham khảo /08_VPS.md

Kiểm tra RAM:

```bash
free -h
```

Nếu RAM ~1GB → nên tạo swap.

---

# PHẦN 2 — Cài Docker chuẩn (không dùng docker.io)

Theo hướng dẫn chính thức từ Docker.

## 2️⃣ Gỡ bản Docker cũ (nếu từng cài)

```bash
sudo apt remove docker docker-engine docker.io containerd runc -y
```

---

## 3️⃣ Cài Docker Engine + Compose v2

```bash
sudo apt update
sudo apt install ca-certificates curl gnupg -y

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

Enable Docker:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

Cho phép user dùng docker không cần sudo:

```bash
sudo usermod -aG docker $USER
```

➡ Sau đó logout SSH và login lại.

---

## 4️⃣ Kiểm tra phiên bản

```bash
docker --version
docker compose version
```

Phải thấy:

- Docker 25+ hoặc 26+
- Docker Compose v2.x

---

# PHẦN 3 — Tạo Swap 2GB (quan trọng cho VPS 1GB RAM)

## 5️⃣ Tạo swap file

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Kiểm tra:

```bash
swapon --show
free -h
```

Phải thấy:

```
Swap: 2.0G
```

## 6️⃣ Tự động bật swap khi reboot

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

//bỏ qua Phần 4 nếu kéo image từ docker hub về vps.
//Trong docker-compose.yml có dạng:

```bash
services:
  app:
    image: username/finance-forecaster:latest
```

# PHẦN 4 — Chuẩn bị Project (not use now)

## 7️⃣ Cài Git

```bash
sudo apt install git -y
```

## 8️⃣ Clone project

```bash
git clone https://github.com/your_repo.git
cd your_repo
```

Hoặc nếu bạn chỉ dùng compose file riêng:

```bash
mkdir -p ~/finance_focaster
cd ~/finance_focaster
```

---

# PHẦN 5 — Cấu hình .env

```bash
nano .env
```

Ví dụ:
Thay xxxx bằng key của bạn.

```env
POSTGRES_PASSWORD=StrongPassword123!

GEMINI_API_KEY=xxxx
TELEGRAM_BOT_TOKEN=xxxx
TELEGRAM_CHAT_ID=xxxx

CRAWL_INTERVAL_HOURS=2
TIMEZONE=Asia/Tokyo
LOG_LEVEL=INFO
```

Lưu file.

---

# PHẦN 6 — Deploy lần đầu

## 9️⃣ Nếu dùng image từ Docker Hub

```bash
docker compose pull
docker compose up -d
```

---

## 🔟 Nếu build local (có Dockerfile) (not use now)

```bash
docker compose build --no-cache
docker compose up -d
```

---

# PHẦN 7 — Kiểm tra hệ thống

Xem container:

```bash
docker compose ps
```

Xem log:

```bash
docker compose logs -f app
```

Xem RAM:

```bash
free -h
```

Xem container dùng bao nhiêu RAM:

```bash
docker stats
```

---

# PHẦN 8 — Quy trình update sau này

## Khi bạn sửa code và push lên GitHub

SSH vào VPS:

```bash
cd your_repo
git pull
```

### Nếu build local: (not use now)

```bash
docker compose down
docker compose build
docker compose up -d
```

### Nếu dùng image từ Docker Hub:

```bash
docker compose pull
docker compose up -d
```

---

# PHẦN 9 — Khi container lỗi

Xem log:

```bash
docker compose logs app
```

Restart:

```bash
docker compose restart
```

Reset toàn bộ:

```bash
docker compose down -v
docker compose up -d
```

---
