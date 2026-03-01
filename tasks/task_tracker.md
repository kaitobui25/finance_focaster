# Finance Forecaster - Task Tracker

## Phase 1: Planning & Architecture
- [x] Đọc và hiểu yêu cầu từ file 02_AGENT_INSTRUCTIONS.md
- [x] Thiết kế Clean Architecture cho project
- [x] Viết file 01_Workflow_Orchestration.md (giữ nguyên workflow rules gốc)
- [x] Viết file 03_Project_Architecture.md (tách riêng kiến trúc)
- [x] Viết implementation_plan.md và chờ user review
- [x] Tạo .gitignore
- [x] Verify RSS feeds hoạt động (3/3 OK)
- [x] Verify Python có sẵn
- [x] User approve plan → bắt đầu implement

## Phase 2: Project Foundation (MVP)
- [x] Tạo cấu trúc thư mục theo Clean Architecture
- [x] Cấu hình môi trường (.env.example, config)
- [x] Thiết kế PostgreSQL schema (10 bảng, tự phản biện 7→10)
- [x] Tạo user `forecaster` + database `finance_forecaster`  
- [x] Chạy `db/init.sql` — 10 bảng, 24 indexes, seed data
- [x] Viết Python adapters cho PostgreSQL (đang chờ)
- [ ] Setup Docker (Dockerfile, docker-compose.yml)

## Phase 3: RSS Crawler Module
- [x] Implement RSS feed parser (feedparser + httpx)
- [x] Implement scheduler (APScheduler)
- [x] Lưu articles vào DB
- [x] Verify crawl 3 feeds thành công (72 articles)

## Phase 4: LLM Analysis Module
- [x] Integrate Google Gemini API (google-genai SDK)
- [x] Implement summarizer (tóm tắt bài viết)
- [x] Implement keyword extractor (từ khóa nổi bật)
- [x] Implement daily digest generator
- [x] Fix: Đổi model `gemini-1.5-flash` → `gemini-2.5-flash`
- [x] Fix: Đồng bộ interface LLMClient với implementation

## Phase 5: Telegram Notification
- [x] Implement console fallback sender
- [x] Setup Telegram Bot (@kai_fina_bot — verified 2026-03-01)
- [x] Implement message formatter (theo format file 02) — verified 2026-03-01
- [x] Implement scheduled report sender (đã có sẵn trong scheduler.py — verified 2026-03-01)

## Phase 6: Verification & Deploy
- [x] Unit tests cho từng module (24/24 passed — 2026-03-01)
- [x] Integration test end-to-end (passed test_integration.py — 2026-03-01)
- [x] Docker build & run test (Dockerfile + docker-compose.yml + GitHub Actions CI — 2026-03-01)
- [x] Deploy guide cho VPS (đã tạo docs/04_DEPLOY_GUIDE_VPS.md — 2026-03-01)
