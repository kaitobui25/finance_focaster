"""Finance Forecaster — Entry point.

Usage:
    python main.py              # Start scheduler (production mode)
    python main.py --run-once   # Run one crawl+analyze+report cycle and exit
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys

from src.infrastructure.config import AppConfig
from src.infrastructure.container import Container
from src.infrastructure.logging_config import setup_logging

logger = logging.getLogger(__name__)


def run_once(container: Container) -> None:
    """Run a single crawl -> analyze -> report cycle."""
    logger.info("=== Running single cycle ===")

    # Step 1: Crawl
    crawl_uc = container.crawl_feeds_use_case()
    new_articles = crawl_uc.execute()
    logger.info("Step 1 done: %d new articles crawled", new_articles)

    # Step 2: Analyze
    analyze_uc = container.analyze_articles_use_case()
    analyzed = analyze_uc.execute()
    logger.info("Step 2 done: %d articles analyzed", analyzed)

    # Step 3: Generate report
    report_uc = container.generate_report_use_case()
    report_uc.execute(report_type="evening")
    logger.info("Step 3 done: report generated and sent")

    logger.info("=== Single cycle complete ===")


def run_scheduler(container: Container) -> None:
    """Start the scheduler for continuous operation."""
    from src.infrastructure.scheduler import create_scheduler

    logger.info("Starting scheduler...")

    # Run an initial crawl+analyze immediately
    crawl_uc = container.crawl_feeds_use_case()
    crawl_uc.execute()

    analyze_uc = container.analyze_articles_use_case()
    analyze_uc.execute()

    # Create and start scheduler
    scheduler = create_scheduler(container, timezone=container._config.timezone)

    # Graceful shutdown
    def shutdown(signum, frame):
        logger.info("Shutdown signal received, stopping scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("Scheduler started. Press Ctrl+C to stop.")
    scheduler.start()


def main() -> None:
    """Application entry point."""
    parser = argparse.ArgumentParser(description="Finance Forecaster")
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run one crawl+analyze+report cycle and exit",
    )
    args = parser.parse_args()

    # Load config
    config = AppConfig.from_env()

    # Setup logging
    setup_logging(config.log_level)
    logger.info("Finance Forecaster starting...")
    logger.info("Timezone: %s", config.timezone)
    logger.info("Telegram: %s", "enabled" if config.telegram_enabled else "disabled (using console)")

    # Create DI container
    container = Container(config)

    if args.run_once:
        run_once(container)
    else:
        run_scheduler(container)


if __name__ == "__main__":
    main()
