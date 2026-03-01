"""Use case: Generate daily report and send notification."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from src.adapters.message_formatter import ReportFormatter
from src.domain.interfaces.repositories import (
    ArticleRepository,
    LLMClient,
    NotificationSender,
    ReportRepository,
)

logger = logging.getLogger(__name__)

# Tokyo timezone offset (UTC+9)
JST = timezone(timedelta(hours=9))


class GenerateReportUseCase:
    """Generate a daily digest report from analyzed articles and send it."""

    def __init__(
        self,
        llm_client: LLMClient,
        article_repo: ArticleRepository,
        report_repo: ReportRepository,
        notification_sender: NotificationSender,
        formatter: ReportFormatter,
    ) -> None:
        self._llm_client = llm_client
        self._article_repo = article_repo
        self._report_repo = report_repo
        self._notification_sender = notification_sender
        self._formatter = formatter

    def execute(self, report_type: str = "evening") -> bool:
        """Generate and send a report.

        Args:
            report_type: "morning" or "evening".

        Returns:
            True if report was generated and sent successfully.
        """
        now = datetime.now(JST)
        today = now.strftime("%Y-%m-%d")

        # Get articles from the last 24 hours
        end = now
        start = now - timedelta(hours=24)

        articles = self._article_repo.find_by_date_range(start, end)

        # Filter only processed articles
        processed = [a for a in articles if a.is_processed and a.summary]

        if not processed:
            logger.warning("No processed articles found for report")
            return False

        logger.info(
            "Generating %s report with %d articles", report_type, len(processed)
        )

        # Build articles data for LLM
        articles_data = [
            {
                "title": a.title,
                "source": a.source,
                "summary": a.summary,
                "keywords": a.keywords,
            }
            for a in processed
        ]

        # Generate digest via LLM (with report_type for correct prompt)
        digest = self._llm_client.generate_digest(articles_data, report_type)

        # Format final report using formatter
        full_report = self._formatter.format(report_type, now, digest)

        # Save to database
        self._report_repo.save(
            {
                "report_date": today,
                "report_type": report_type,
                "content": full_report,
            }
        )

        # Send notification
        success = self._notification_sender.send(full_report)

        if success:
            logger.info("%s report sent successfully", report_type.capitalize())
        else:
            logger.error("Failed to send %s report", report_type)

        return success
