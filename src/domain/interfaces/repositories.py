"""Abstract interfaces for the Finance Forecaster application.

These interfaces define contracts that adapters must implement.
Domain and use cases depend ONLY on these interfaces, never on concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.entities.article import Article, FeedSource


class FeedParser(ABC):
    """Interface for parsing RSS feeds."""

    @abstractmethod
    def parse(self, feed_source: FeedSource) -> list[Article]:
        """Parse a feed source and return a list of articles."""


class ArticleRepository(ABC):
    """Interface for article persistence."""

    @abstractmethod
    def save(self, article: Article) -> Article:
        """Save an article. Returns the saved article with ID."""

    @abstractmethod
    def exists_by_link(self, link: str) -> bool:
        """Check if an article with given link already exists."""

    @abstractmethod
    def find_unprocessed(self) -> list[Article]:
        """Find all articles that haven't been processed yet."""

    @abstractmethod
    def mark_processed(self, article_id: int, summary: str, keywords: list[str]) -> None:
        """Mark an article as processed with its summary and keywords."""

    @abstractmethod
    def find_by_date_range(self, start: datetime, end: datetime) -> list[Article]:
        """Find all articles within a date range."""


class ReportRepository(ABC):
    """Interface for report persistence."""

    @abstractmethod
    def save(self, report: dict) -> None:
        """Save a report."""

    @abstractmethod
    def find_by_date(self, report_date: str, report_type: str) -> dict | None:
        """Find a report by date and type."""


class LLMClient(ABC):
    """Interface for LLM interactions."""

    @abstractmethod
    def summarize(self, text: str, title: str = "") -> str:
        """Summarize a text. Returns the summary."""

    @abstractmethod
    def extract_keywords(self, text: str, title: str = "") -> list[str]:
        """Extract keywords from a text. Returns list of keywords."""

    @abstractmethod
    def generate_digest(self, articles_data: list[dict]) -> str:
        """Generate a daily digest from a list of analyzed articles."""


class NotificationSender(ABC):
    """Interface for sending notifications."""

    @abstractmethod
    def send(self, message: str) -> bool:
        """Send a message. Returns True if successful."""
