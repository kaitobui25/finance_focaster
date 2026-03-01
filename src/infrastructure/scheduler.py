"""Scheduler for periodic jobs.

Uses APScheduler to run crawl, analysis, and report generation on a schedule.
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.infrastructure.container import Container

logger = logging.getLogger(__name__)


def _job_crawl_and_analyze(container: Container) -> None:
    """Job: Crawl feeds then analyze new articles."""
    try:
        logger.info("--- Starting scheduled crawl + analysis ---")
        crawl_uc = container.crawl_feeds_use_case()
        new_count = crawl_uc.execute()

        if new_count > 0:
            analyze_uc = container.analyze_articles_use_case()
            analyze_uc.execute()

        logger.info("--- Crawl + analysis cycle complete ---")
    except Exception as exc:
        logger.error("Scheduled crawl+analyze failed: %s", exc)


def _job_morning_report(container: Container) -> None:
    """Job: Generate and send morning report."""
    try:
        logger.info("--- Generating morning report ---")
        report_uc = container.generate_report_use_case()
        report_uc.execute(report_type="morning")
    except Exception as exc:
        logger.error("Morning report failed: %s", exc)


def _job_evening_report(container: Container) -> None:
    """Job: Generate and send evening report."""
    try:
        logger.info("--- Generating evening report ---")
        report_uc = container.generate_report_use_case()
        report_uc.execute(report_type="evening")
    except Exception as exc:
        logger.error("Evening report failed: %s", exc)


def create_scheduler(container: Container, timezone: str = "Asia/Tokyo") -> BlockingScheduler:
    """Create and configure the scheduler with all jobs.

    Args:
        container: DI container with all dependencies.
        timezone: Timezone for cron triggers.

    Returns:
        Configured scheduler (not yet started).
    """
    scheduler = BlockingScheduler(timezone=timezone)

    crawl_hours = container._config.crawl_interval_hours

    # Crawl + Analyze every N hours
    scheduler.add_job(
        _job_crawl_and_analyze,
        trigger=IntervalTrigger(hours=crawl_hours),
        args=[container],
        id="crawl_and_analyze",
        name=f"Crawl + Analyze (every {crawl_hours}h)",
        misfire_grace_time=300,
    )

    # Morning report
    morning_h, morning_m = container._config.morning_report_time.split(":")
    scheduler.add_job(
        _job_morning_report,
        trigger=CronTrigger(hour=int(morning_h), minute=int(morning_m)),
        args=[container],
        id="morning_report",
        name=f"Morning Report ({morning_h}:{morning_m} JST)",
        misfire_grace_time=600,
    )

    # Evening report
    evening_h, evening_m = container._config.evening_report_time.split(":")
    scheduler.add_job(
        _job_evening_report,
        trigger=CronTrigger(hour=int(evening_h), minute=int(evening_m)),
        args=[container],
        id="evening_report",
        name=f"Evening Report ({evening_h}:{evening_m} JST)",
        misfire_grace_time=600,
    )

    logger.info("Scheduler configured with %d jobs", len(scheduler.get_jobs()))
    return scheduler
