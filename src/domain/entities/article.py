"""Domain entities for the Finance Forecaster application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FeedSource:
    """Represents an RSS feed source configuration."""

    name: str
    url: str
    category: str
    language: str = "en"


@dataclass
class Article:
    """Represents a news article fetched from an RSS feed."""

    title: str
    link: str
    source: str
    category: str = "general"
    language: str = "en"
    published_at: datetime | None = None
    content: str = ""
    summary: str = ""
    keywords: list[str] = field(default_factory=list)
    is_processed: bool = False
    id: int | None = None
    created_at: datetime | None = None


@dataclass
class DailyReport:
    """Represents a generated daily report."""

    report_date: str
    report_type: str  # "morning" | "evening"
    content: str
    id: int | None = None
    created_at: datetime | None = None
