# 03_Project_Architecture.md
# Finance Forecaster — Kiến Trúc Dự Án

> Phiên bản: 1.0 | Cập nhật: 2026-03-01

---

## 1. CẤU TRÚC THƯ MỤC (Clean Architecture)

```
finance_forecaster/
├── docs/                          # Tài liệu dự án
│   ├── 01_Workflow_Orchestration.md
│   ├── 02_AGENT_INSTRUCTIONS.md
│   └── 03_Project_Architecture.md
│
├── src/                           # Source code chính
│   ├── domain/                    # Layer 1: Business entities & rules
│   │   ├── entities/              # Data models (Article, Report, Feed...)
│   │   └── interfaces/           # Abstract interfaces (repositories, services)
│   │
│   ├── use_cases/                 # Layer 2: Application business logic
│   │   ├── crawl_feeds.py        # UC: Thu thập RSS feeds
│   │   ├── analyze_articles.py   # UC: Phân tích bài viết bằng LLM
│   │   └── generate_report.py    # UC: Tạo báo cáo tổng hợp
│   │
│   ├── adapters/                  # Layer 3: Interface adapters
│   │   ├── rss_parser.py         # Adapter: Parse RSS feed
│   │   ├── gemini_client.py      # Adapter: Gọi Gemini API
│   │   ├── telegram_sender.py    # Adapter: Gửi tin Telegram
│   │   └── postgres_repository.py# Adapter: PostgreSQL repository
│   │
│   └── infrastructure/            # Layer 4: External frameworks & drivers
│       ├── config.py              # App configuration
│       ├── database.py            # DB connection & session
│       ├── scheduler.py           # APScheduler setup
│       ├── container.py           # Dependency Injection wiring
│       └── logging_config.py      # Logging configuration
│
├── tasks/                         # Task tracking
│   ├── todo.md
│   └── lessons.md
│
├── tests/                         # Unit & integration tests
├── db/                            # Database migrations
│   └── init.sql
│
├── docker/                        # Cấu hình Docker
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── .dockerignore
│
├── requirements.txt
├── feeds.yaml                     # RSS feeds config (dễ thêm/bớt)
├── .env.example
├── main.py                        # Entry point
└── README.md
```

---

## 2. DEPENDENCY RULE

```
Domain ← Use Cases ← Adapters ← Infrastructure
(trong)                              (ngoài)
```

- **Domain** không phụ thuộc bất cứ layer nào khác
- **Use Cases** chỉ phụ thuộc Domain (qua interfaces)
- **Adapters** implement interfaces từ Domain
- **Infrastructure** wiring mọi thứ lại (dependency injection)

---

## 3. QUẢN LÝ CẤU HÌNH

- Tất cả secrets (API keys, tokens) lưu trong `.env`, **không bao giờ commit**
- File `.env.example` chứa template với giá trị mẫu
- Config class đọc từ environment variables, có validation

---

## 4. LOGGING & ERROR HANDLING

- Dùng Python `logging` module, không `print()`
- Log levels: DEBUG → INFO → WARNING → ERROR → CRITICAL
- Mọi external call (API, DB, RSS) phải có try-except và retry logic
- Log format: `[TIMESTAMP] [LEVEL] [MODULE] message`

---

## 5. PHÁT TRIỂN THEO PHASE

| Phase | Nội dung | Trạng thái |
|---|---|---|
| **Phase 1 — MVP** | RSS Crawler → LLM Summarize + Keywords → Telegram | Đang triển khai |
| **Phase 2** | Thêm 4 framework phân tích + Market Data APIs | Chưa bắt đầu |
| **Phase 3** | Automated recommendations + Portfolio tracking | Chưa bắt đầu |
| **Phase 4** | Web dashboard + Visualization (tùy chọn) | Chưa bắt đầu |

---

*File này mô tả kiến trúc kỹ thuật của dự án Finance Forecaster.*
*Cập nhật khi có thay đổi kiến trúc hoặc chuyển phase.*
