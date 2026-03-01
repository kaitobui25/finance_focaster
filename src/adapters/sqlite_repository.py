"""SQLite repository adapter.

Implements ArticleRepository and ReportRepository interfaces using SQLite.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

from src.domain.entities.article import Article
from src.domain.interfaces.repositories import ArticleRepository, ReportRepository
from src.infrastructure.database import Database

logger = logging.getLogger(__name__)


class SQLiteArticleRepository(ArticleRepository):
    """Article repository implementation using SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def save(self, article: Article) -> Article:
        """Save an article to the database."""
        with self._db.connect() as conn:
            cursor = conn.execute(
                """INSERT INTO articles (title, link, source, published_at, content)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    article.title,
                    article.link,
                    article.source,
                    article.published_at.isoformat() if article.published_at else None,
                    article.content,
                ),
            )
            conn.commit()
            article.id = cursor.lastrowid
            logger.debug("Saved article: %s (ID: %d)", article.title[:50], article.id)
            return article

    def exists_by_link(self, link: str) -> bool:
        """Check if an article with given link already exists."""
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM articles WHERE link = ?", (link,)
            ).fetchone()
            return row is not None

    def find_unprocessed(self) -> list[Article]:
        """Find all articles that haven't been processed yet."""
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM articles WHERE is_processed = 0 ORDER BY published_at DESC"
            ).fetchall()
            return [self._row_to_article(row) for row in rows]

    def mark_processed(
        self, article_id: int, summary: str, keywords: list[str]
    ) -> None:
        """Mark an article as processed with its summary and keywords."""
        with self._db.connect() as conn:
            conn.execute(
                """UPDATE articles
                   SET is_processed = 1, summary = ?, keywords = ?
                   WHERE id = ?""",
                (summary, json.dumps(keywords), article_id),
            )
            conn.commit()
            logger.debug("Marked article %d as processed", article_id)

    def find_by_date_range(
        self, start: datetime, end: datetime
    ) -> list[Article]:
        """Find all articles within a date range."""
        with self._db.connect() as conn:
            rows = conn.execute(
                """SELECT * FROM articles
                   WHERE published_at BETWEEN ? AND ?
                   ORDER BY published_at DESC""",
                (start.isoformat(), end.isoformat()),
            ).fetchall()
            return [self._row_to_article(row) for row in rows]

    def _row_to_article(self, row: dict) -> Article:
        """Convert a database row to an Article entity."""
        keywords = []
        raw_keywords = row["keywords"]
        if raw_keywords:
            try:
                keywords = json.loads(raw_keywords)
            except json.JSONDecodeError:
                keywords = []

        published_at = None
        if row["published_at"]:
            try:
                published_at = datetime.fromisoformat(row["published_at"])
            except ValueError:
                pass

        return Article(
            id=row["id"],
            title=row["title"],
            link=row["link"],
            source=row["source"],
            published_at=published_at,
            content=row["content"] or "",
            summary=row["summary"] or "",
            keywords=keywords,
            is_processed=bool(row["is_processed"]),
            created_at=None,
        )


class SQLiteReportRepository(ReportRepository):
    """Report repository implementation using SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def save(self, report: dict) -> None:
        """Save a report to the database."""
        with self._db.connect() as conn:
            conn.execute(
                """INSERT INTO reports (report_date, report_type, content)
                   VALUES (?, ?, ?)""",
                (report["report_date"], report["report_type"], report["content"]),
            )
            conn.commit()
            logger.info(
                "Saved %s report for %s",
                report["report_type"],
                report["report_date"],
            )

    def find_by_date(self, report_date: str, report_type: str) -> dict | None:
        """Find a report by date and type."""
        with self._db.connect() as conn:
            row = conn.execute(
                """SELECT * FROM reports
                   WHERE report_date = ? AND report_type = ?
                   ORDER BY created_at DESC LIMIT 1""",
                (report_date, report_type),
            ).fetchone()

            if row:
                return dict(row)
            return None
