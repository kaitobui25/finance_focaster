"""PostgreSQL repository adapter.

Implements ArticleRepository and ReportRepository interfaces using PostgreSQL.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from src.domain.entities.article import Article
from src.domain.interfaces.repositories import ArticleRepository, ReportRepository
from src.infrastructure.database import Database

logger = logging.getLogger(__name__)


class PostgresArticleRepository(ArticleRepository):
    """Article repository implementation using PostgreSQL."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def save(self, article: Article) -> Article:
        """Save an article to the database."""
        with self._db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO articles
                       (title, link, source, category, language, published_at, content)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       RETURNING id""",
                    (
                        article.title,
                        article.link,
                        article.source,
                        article.category,
                        article.language,
                        article.published_at,
                        article.content,
                    ),
                )
                article.id = cur.fetchone()["id"]
                logger.debug("Saved article: %s (ID: %d)", article.title[:50], article.id)
                return article

    def exists_by_link(self, link: str) -> bool:
        """Check if an article with given link already exists."""
        with self._db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM articles WHERE link = %s", (link,))
                return cur.fetchone() is not None

    def find_unprocessed(self) -> list[Article]:
        """Find all articles that haven't been processed yet."""
        with self._db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM articles
                       WHERE is_processed = FALSE
                       ORDER BY published_at DESC"""
                )
                return [self._row_to_article(row) for row in cur.fetchall()]

    def mark_processed(
        self, article_id: int, summary: str, keywords: list[str]
    ) -> None:
        """Mark an article as processed with its summary and keywords."""
        with self._db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE articles
                       SET is_processed = TRUE, summary = %s, keywords = %s
                       WHERE id = %s""",
                    (summary, json.dumps(keywords), article_id),
                )
                logger.debug("Marked article %d as processed", article_id)

    def find_by_date_range(
        self, start: datetime, end: datetime
    ) -> list[Article]:
        """Find all articles within a date range."""
        with self._db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM articles
                       WHERE published_at BETWEEN %s AND %s
                       ORDER BY published_at DESC""",
                    (start.isoformat(), end.isoformat()),
                )
                return [self._row_to_article(row) for row in cur.fetchall()]

    def _row_to_article(self, row: dict) -> Article:
        """Convert a database row to an Article entity."""
        keywords = row["keywords"] if isinstance(row["keywords"], list) else []

        return Article(
            id=row["id"],
            title=row["title"],
            link=row["link"],
            source=row["source"],
            category=row.get("category", "general"),
            language=row.get("language", "en"),
            published_at=row["published_at"],
            content=row["content"] or "",
            summary=row["summary"] or "",
            keywords=keywords,
            is_processed=bool(row["is_processed"]),
            created_at=row.get("created_at"),
        )


class PostgresReportRepository(ReportRepository):
    """Report repository implementation using PostgreSQL."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def save(self, report: dict) -> None:
        """Save a report to the database."""
        with self._db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO reports (report_date, report_type, content)
                       VALUES (%s, %s, %s)""",
                    (report["report_date"], report["report_type"], report["content"]),
                )
                logger.info(
                    "Saved %s report for %s",
                    report["report_type"],
                    report["report_date"],
                )

    def find_by_date(self, report_date: str, report_type: str) -> dict | None:
        """Find a report by date and type."""
        with self._db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM reports
                       WHERE report_date = %s AND report_type = %s
                       ORDER BY created_at DESC LIMIT 1""",
                    (report_date, report_type),
                )
                row = cur.fetchone()
                return dict(row) if row else None
