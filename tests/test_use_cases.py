"""Unit tests for Use Cases (CrawlFeeds, AnalyzeArticles, GenerateReport).

All external dependencies are mocked. No DB, no API calls.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

from src.domain.entities.article import Article, FeedSource
from src.adapters.message_formatter import ReportFormatter
from src.use_cases.crawl_feeds import CrawlFeedsUseCase
from src.use_cases.analyze_articles import AnalyzeArticlesUseCase
from src.use_cases.generate_report import GenerateReportUseCase

JST = timezone(timedelta(hours=9))


def _make_article(
    title="Test Article",
    link="https://example.com/1",
    source="TestSource",
    is_processed=False,
    summary="",
    keywords=None,
    article_id=1,
) -> Article:
    """Helper to create test Article."""
    return Article(
        title=title,
        link=link,
        source=source,
        category="general",
        language="en",
        published_at=datetime.now(JST),
        content="Some article content",
        summary=summary,
        keywords=keywords or [],
        is_processed=is_processed,
        id=article_id,
    )


# ── CrawlFeedsUseCase ─────────────────────────────────────────────


class TestCrawlFeedsUseCase:
    """Tests for CrawlFeedsUseCase."""

    def setup_method(self):
        self.parser = MagicMock()
        self.repo = MagicMock()
        self.uc = CrawlFeedsUseCase(
            feed_parser=self.parser,
            article_repo=self.repo,
            feeds_config_path="tests/fixtures/test_feeds.yaml",
        )

    @patch("builtins.open", create=True)
    @patch("yaml.safe_load")
    def test_saves_new_articles(self, mock_yaml, mock_open):
        mock_yaml.return_value = {
            "feeds": [{"name": "Test", "url": "https://example.com/rss", "category": "test"}]
        }
        articles = [_make_article(link="https://example.com/new")]
        self.parser.parse.return_value = articles
        self.repo.exists_by_link.return_value = False

        result = self.uc.execute()

        assert result == 1
        self.repo.save.assert_called_once()

    @patch("builtins.open", create=True)
    @patch("yaml.safe_load")
    def test_skips_existing_articles(self, mock_yaml, mock_open):
        mock_yaml.return_value = {
            "feeds": [{"name": "Test", "url": "https://example.com/rss", "category": "test"}]
        }
        self.parser.parse.return_value = [_make_article()]
        self.repo.exists_by_link.return_value = True

        result = self.uc.execute()

        assert result == 0
        self.repo.save.assert_not_called()

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_handles_missing_config(self, mock_open):
        result = self.uc.execute()
        assert result == 0


# ── AnalyzeArticlesUseCase ────────────────────────────────────────


class TestAnalyzeArticlesUseCase:
    """Tests for AnalyzeArticlesUseCase."""

    def setup_method(self):
        self.llm = MagicMock()
        self.repo = MagicMock()
        self.uc = AnalyzeArticlesUseCase(
            llm_client=self.llm,
            article_repo=self.repo,
        )

    def test_analyzes_unprocessed_articles(self):
        articles = [_make_article(article_id=1), _make_article(article_id=2, link="https://example.com/2")]
        self.repo.find_unprocessed.return_value = articles
        self.llm.summarize.return_value = "Summary text"
        self.llm.extract_keywords.return_value = ["keyword1", "keyword2"]

        result = self.uc.execute()

        assert result == 2
        assert self.repo.mark_processed.call_count == 2

    def test_returns_zero_when_no_articles(self):
        self.repo.find_unprocessed.return_value = []

        result = self.uc.execute()

        assert result == 0
        self.llm.summarize.assert_not_called()

    def test_continues_on_error(self):
        articles = [_make_article(article_id=1), _make_article(article_id=2, link="https://example.com/2")]
        self.repo.find_unprocessed.return_value = articles
        self.llm.summarize.side_effect = [Exception("API Error"), "Good summary"]
        self.llm.extract_keywords.return_value = ["kw"]

        result = self.uc.execute()

        assert result == 1  # Only the second one succeeds


# ── GenerateReportUseCase ─────────────────────────────────────────


class TestGenerateReportUseCase:
    """Tests for GenerateReportUseCase."""

    def setup_method(self):
        self.llm = MagicMock()
        self.article_repo = MagicMock()
        self.report_repo = MagicMock()
        self.sender = MagicMock()
        self.formatter = ReportFormatter()
        self.uc = GenerateReportUseCase(
            llm_client=self.llm,
            article_repo=self.article_repo,
            report_repo=self.report_repo,
            notification_sender=self.sender,
            formatter=self.formatter,
        )

    def test_generates_and_sends_report(self):
        processed_article = _make_article(
            is_processed=True, summary="A summary", keywords=["BOJ"]
        )
        self.article_repo.find_by_date_range.return_value = [processed_article]
        self.llm.generate_digest.return_value = "📊 KẾT QUẢ PHIÊN\n• Nikkei 225: 40,000"
        self.sender.send.return_value = True

        result = self.uc.execute(report_type="evening")

        assert result is True
        self.llm.generate_digest.assert_called_once()
        self.report_repo.save.assert_called_once()
        self.sender.send.assert_called_once()

        # Verify formatted report contains expected elements
        sent_msg = self.sender.send.call_args[0][0]
        assert "🌙 KAI-FINA | End-of-Day Report" in sent_msg
        assert "📊 KẾT QUẢ PHIÊN" in sent_msg
        assert "⚠️ DISCLAIMER" in sent_msg

    def test_returns_false_when_no_articles(self):
        self.article_repo.find_by_date_range.return_value = []

        result = self.uc.execute()

        assert result is False
        self.llm.generate_digest.assert_not_called()

    def test_passes_report_type_to_llm(self):
        processed_article = _make_article(
            is_processed=True, summary="Summary", keywords=["test"]
        )
        self.article_repo.find_by_date_range.return_value = [processed_article]
        self.llm.generate_digest.return_value = "digest"
        self.sender.send.return_value = True

        self.uc.execute(report_type="morning")

        # Verify report_type was passed to LLM
        call_args = self.llm.generate_digest.call_args
        assert call_args[0][1] == "morning" or call_args[1].get("report_type") == "morning"

    def test_returns_false_when_send_fails(self):
        processed_article = _make_article(
            is_processed=True, summary="Summary", keywords=["test"]
        )
        self.article_repo.find_by_date_range.return_value = [processed_article]
        self.llm.generate_digest.return_value = "digest"
        self.sender.send.return_value = False

        result = self.uc.execute()

        assert result is False
