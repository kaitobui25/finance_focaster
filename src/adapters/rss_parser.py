"""RSS feed parser adapter.

Implements FeedParser interface using the feedparser library.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import feedparser
import httpx

from src.domain.entities.article import Article, FeedSource
from src.domain.interfaces.repositories import FeedParser

logger = logging.getLogger(__name__)


class FeedparserRSSParser(FeedParser):
    """RSS parser implementation using feedparser + httpx."""

    def __init__(self, timeout: int = 30) -> None:
        self._timeout = timeout

    def parse(self, feed_source: FeedSource) -> list[Article]:
        """Fetch and parse an RSS feed into a list of Articles."""
        try:
            logger.info("Fetching feed: %s (%s)", feed_source.name, feed_source.url)

            response = httpx.get(
                feed_source.url,
                timeout=self._timeout,
                follow_redirects=True,
                headers={"User-Agent": "FinanceForecaster/1.0"},
            )
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            if feed.bozo and not feed.entries:
                logger.warning(
                    "Feed parsing error for %s: %s",
                    feed_source.name,
                    feed.bozo_exception,
                )
                return []

            articles = []
            for entry in feed.entries:
                article = self._entry_to_article(entry, feed_source)
                if article:
                    articles.append(article)

            logger.info(
                "Parsed %d articles from %s", len(articles), feed_source.name
            )
            return articles

        except httpx.HTTPError as exc:
            logger.error("HTTP error fetching %s: %s", feed_source.name, exc)
            return []
        except Exception as exc:
            logger.error("Unexpected error parsing %s: %s", feed_source.name, exc)
            return []

    def _entry_to_article(
        self, entry: dict, feed_source: FeedSource
    ) -> Article | None:
        """Convert a feedparser entry to an Article entity."""
        title = getattr(entry, "title", "").strip()
        link = getattr(entry, "link", "").strip()

        if not title or not link:
            return None

        # Skip category/section pages (no real content)
        if len(title) < 10 and not getattr(entry, "description", ""):
            return None

        # Parse publish date
        published_at = self._parse_date(entry)

        # Extract content from description
        content = self._extract_content(entry)

        return Article(
            title=title,
            link=link,
            source=feed_source.name,
            category=feed_source.category,
            language=feed_source.language,
            published_at=published_at,
            content=content,
        )

    def _parse_date(self, entry: dict) -> datetime | None:
        """Parse the publication date from a feed entry."""
        date_fields = ["published_parsed", "updated_parsed"]

        for field in date_fields:
            parsed = getattr(entry, field, None)
            if parsed:
                try:
                    return datetime(*parsed[:6], tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_content(self, entry: dict) -> str:
        """Extract readable content from a feed entry."""
        # Try content field first
        content_list = getattr(entry, "content", [])
        if content_list:
            raw = content_list[0].get("value", "")
            return self._strip_html(raw)

        # Fall back to description/summary
        description = getattr(entry, "description", "") or getattr(
            entry, "summary", ""
        )
        return self._strip_html(description)

    def _strip_html(self, html: str) -> str:
        """Remove HTML tags from a string. Simple regex-free approach."""
        result = []
        in_tag = False
        for char in html:
            if char == "<":
                in_tag = True
            elif char == ">":
                in_tag = False
            elif not in_tag:
                result.append(char)
        return "".join(result).strip()
