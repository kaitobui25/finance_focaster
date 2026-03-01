"""Use case: Crawl RSS feeds and save new articles to the database."""

from __future__ import annotations

import logging

import yaml

from src.domain.entities.article import FeedSource
from src.domain.interfaces.repositories import ArticleRepository, FeedParser

logger = logging.getLogger(__name__)


class CrawlFeedsUseCase:
    """Crawl configured RSS feeds and persist new articles."""

    def __init__(
        self,
        feed_parser: FeedParser,
        article_repo: ArticleRepository,
        feeds_config_path: str,
    ) -> None:
        self._feed_parser = feed_parser
        self._article_repo = article_repo
        self._feeds_config_path = feeds_config_path

    def execute(self) -> int:
        """Run the crawl. Returns the number of new articles saved."""
        feed_sources = self._load_feeds()
        total_new = 0

        for source in feed_sources:
            articles = self._feed_parser.parse(source)

            for article in articles:
                if not self._article_repo.exists_by_link(article.link):
                    self._article_repo.save(article)
                    total_new += 1

        logger.info("Crawl complete: %d new articles saved", total_new)
        return total_new

    def _load_feeds(self) -> list[FeedSource]:
        """Load feed sources from YAML configuration."""
        try:
            with open(self._feeds_config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            feeds = []
            for feed_data in config.get("feeds", []):
                feeds.append(
                    FeedSource(
                        name=feed_data["name"],
                        url=feed_data["url"],
                        category=feed_data.get("category", "general"),
                        language=feed_data.get("language", "en"),
                    )
                )
            logger.info("Loaded %d feed sources from config", len(feeds))
            return feeds

        except FileNotFoundError:
            logger.error("Feeds config not found: %s", self._feeds_config_path)
            return []
        except yaml.YAMLError as exc:
            logger.error("Error parsing feeds config: %s", exc)
            return []
