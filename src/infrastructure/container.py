"""Dependency injection container.

Wires all concrete implementations to their interfaces.
This is the only place where concrete classes are instantiated.
"""

from __future__ import annotations

import logging

from src.adapters.gemini_client import GeminiLLMClient
from src.adapters.rss_parser import FeedparserRSSParser
from src.adapters.postgres_repository import PostgresArticleRepository, PostgresReportRepository
from src.adapters.telegram_sender import ConsoleNotificationSender, TelegramNotificationSender
from src.infrastructure.config import AppConfig
from src.infrastructure.database import Database
from src.use_cases.analyze_articles import AnalyzeArticlesUseCase
from src.use_cases.crawl_feeds import CrawlFeedsUseCase
from src.use_cases.generate_report import GenerateReportUseCase

logger = logging.getLogger(__name__)


class Container:
    """Dependency injection container.

    Creates and holds all application components.
    Single source of truth for wiring.
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config

        # Infrastructure
        self._database = Database(config.database_url)

        # Adapters
        self._feed_parser = FeedparserRSSParser()
        self._llm_client = GeminiLLMClient(config.gemini_api_key)
        self._article_repo = PostgresArticleRepository(self._database)
        self._report_repo = PostgresReportRepository(self._database)
        self._notification_sender = self._create_notification_sender()

        logger.info("Container initialized successfully")

    def _create_notification_sender(self):
        """Create the appropriate notification sender based on config."""
        if self._config.telegram_enabled:
            logger.info("Telegram notifications enabled")
            return TelegramNotificationSender(
                self._config.telegram_bot_token,
                self._config.telegram_chat_id,
            )

        logger.info("Telegram not configured — using console output")
        return ConsoleNotificationSender()

    # --- Use Case factories ---

    def crawl_feeds_use_case(self) -> CrawlFeedsUseCase:
        """Create CrawlFeedsUseCase with all dependencies."""
        return CrawlFeedsUseCase(
            feed_parser=self._feed_parser,
            article_repo=self._article_repo,
            feeds_config_path=self._config.feeds_config_path,
        )

    def analyze_articles_use_case(self) -> AnalyzeArticlesUseCase:
        """Create AnalyzeArticlesUseCase with all dependencies."""
        return AnalyzeArticlesUseCase(
            llm_client=self._llm_client,
            article_repo=self._article_repo,
        )

    def generate_report_use_case(self) -> GenerateReportUseCase:
        """Create GenerateReportUseCase with all dependencies."""
        return GenerateReportUseCase(
            llm_client=self._llm_client,
            article_repo=self._article_repo,
            report_repo=self._report_repo,
            notification_sender=self._notification_sender,
        )
