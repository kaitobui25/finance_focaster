"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


@dataclass
class AppConfig:
    """Central configuration for the application.

    Reads from environment variables with sensible defaults.
    """

    # LLM
    gemini_api_key: str = ""

    # Database
    database_url: str = "sqlite:///data/finance_forecaster.db"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Scheduler
    crawl_interval_hours: int = 2
    morning_report_time: str = "07:45"
    evening_report_time: str = "16:30"

    # General
    timezone: str = "Asia/Tokyo"
    log_level: str = "INFO"

    # Feeds config path
    feeds_config_path: str = ""

    @classmethod
    def from_env(cls) -> AppConfig:
        """Create config from environment variables."""
        config = cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            database_url=os.getenv("DATABASE_URL", "sqlite:///data/finance_forecaster.db"),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            crawl_interval_hours=int(os.getenv("CRAWL_INTERVAL_HOURS", "2")),
            morning_report_time=os.getenv("MORNING_REPORT_TIME", "07:45"),
            evening_report_time=os.getenv("EVENING_REPORT_TIME", "16:30"),
            timezone=os.getenv("TIMEZONE", "Asia/Tokyo"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            feeds_config_path=str(_PROJECT_ROOT / "feeds.yaml"),
        )
        config.validate()
        return config

    def validate(self) -> None:
        """Validate required configuration."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file.")

    @property
    def telegram_enabled(self) -> bool:
        """Check if Telegram is configured."""
        return bool(self.telegram_bot_token and self.telegram_chat_id)
