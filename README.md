# Finance Forecaster

Finance Forecaster is an AI-powered financial market intelligence system built on Clean Architecture principles. It autonomously crawls global financial news, analyzes market sentiment using Google's Gemini LLM, stores structured intelligence in a robust PostgreSQL database, and delivers concise, actionable reports to investors.

## Key Features

- **Automated Intelligence Gathering**: Crawls RSS feeds from trusted sources (Japan Times, Nikkei Asia, Reuters) to aggregate real-time financial news.
- **Deep AI Analysis**: Leverages Google Gemini 2.5 Flash to process raw news into concise summaries, isolate key entities, and determine actionable market tags.
- **Comprehensive Data Storage**: Uses a fully-featured 10-table PostgreSQL schema to track not just articles, but also financial instruments, market snapshots, sector performance, and AI-generated trading recommendations.
- **Automated Reporting**: Generates "Pre-Market Briefs" and "End-of-Day Reports" analyzing macro events and their specific impact on Japanese equities (Nikkei/TOPIX), safe-haven assets (JPY/Gold), and broader global markets.
- **Flexible Execution**: Can be run once for an immediate cycle or as a continuous background scheduler prioritizing different times of the day.

## Tech Stack

- **Language**: Python 3.10+
- **Database**: PostgreSQL 18+ (`psycopg2-binary`)
- **AI Integration**: Google GenAI SDK (`google-genai`)
- **Networking/Crawling**: `httpx`, `feedparser`
- **Scheduling**: `apscheduler`
- **Architecture**: Domain-Driven Design (Clean Architecture)

## Project Structure (Clean Architecture)

```
finance_forecaster/
├── db/                     # Database schemas and documentation
│   ├── init.sql            # PostgreSQL 10-table DDL and seed data
│   └── README.md           # Database tables explained
├── docs/                   # Architectural instructions and agent rules
├── src/                    # Core application source code
│   ├── adapters/           # External API & DB implementations (PostgreSQL, Gemini, RSS)
│   ├── domain/             # Core business entities and interfaces
│   ├── infrastructure/     # Wiring, DI Container, Logging, Config
│   └── use_cases/          # Business logic orchestrators
├── feeds.yaml              # RSS feed configuration
├── main.py                 # Application entry point
├── .env.example            # Environment variables template
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- PostgreSQL Server 18.x running locally (or via Docker)
- A valid Google Gemini API Key

### 2. Installation
Clone the repository, create a virtual environment, and install dependencies:
```bash
python -m venv venv
.\venv\Scripts\activate   # (Windows)
# source venv/bin/activate # (Mac/Linux)

pip install -r requirements.txt
```

### 3. Configuration
Copy the environment template and configure your keys:
```bash
cp .env.example .env
```
Open `.env` and fill in your details:
- `GEMINI_API_KEY`: Your Google Gemini API key.
- `DATABASE_URL`: Ensure it points to your local PostgreSQL instance (default is `postgresql://forecaster:1111@localhost:5432/finance_forecaster`).
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID`: (Optional) Tokens to receive reports on Telegram.

### 4. Database Initialization
Ensure your PostgreSQL server is running. Create a superuser or the `forecaster` user if it doesn't exist, and run the initialization script:
```bash
# Example via psql command line:
psql -U postgres -f db/init.sql
```

## Usage

### Run a Single Cycle (Crawl -> Analyze -> Report)
This command fetches fresh RSS feeds, asks Gemini to process any unanalyzed articles, generates the latest report, and saves/sends it.
```bash
python main.py --run-once
```

### Run as a Continuous Service
This command starts the internal APScheduler. It will continuously monitor the feeds every few hours and generate morning/evening reports exactly on schedule.
```bash
python main.py
```

## Architecture Design

The system follows **Clean Architecture**, aggressively separating business logic from infrastructure concerns:
- **Domain**: Pure Python dataclasses (`Article`, `DailyReport`) and ABC interfaces (`ArticleRepository`, `FeedParser`). Zero external dependencies.
- **Use Cases**: Contains the application logic (`CrawlFeedsUseCase`, `AnalyzeArticlesUseCase`). Operates solely on Domain interfaces.
- **Adapters**: Implements Domain interfaces connecting to the outside world (`PostgresArticleRepository`, `GeminiLLMClient`).
- **Infrastructure**: Handles dependency injection (`Container`), database string connections, and log setup.

## Roadmap & Next Steps
- Implement full Telegram notification integration.
- Finalize Dockerization (`Dockerfile`, `docker-compose.yml`) for seamless deployment.
- Integrate automated end-to-end testing with `pytest`.
