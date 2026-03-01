"""Integration tests for the full application pipeline.

This test uses the real database but mocks external network calls
(RSS fetching, Gemini API, and Telegram API) to verify that all
components wire together and function correctly end-to-end.
"""

import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

import pytest

from src.infrastructure.config import AppConfig
from src.infrastructure.container import Container
from src.domain.entities.article import Article

JST = timezone(timedelta(hours=9))


@pytest.fixture
def test_config():
    """Provides configuration for testing, using the real DB."""
    # We use the actual dev database for integration testing
    # In a real CI environment, this would be a dedicated test DB
    os.environ.setdefault("DATABASE_URL", "postgresql://forecaster:1111@localhost:5432/finance_forecaster")
    os.environ.setdefault("GEMINI_API_KEY", "test_gemini_key")
    os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_bot_token")
    os.environ.setdefault("TELEGRAM_CHAT_ID", "12345")
    os.environ.setdefault("FEEDS_CONFIG_PATH", "config/feeds.yaml")
    return AppConfig.from_env()


@pytest.fixture
def container(test_config):
    """Provides a wired DI container."""
    return Container(test_config)


@pytest.fixture(autouse=True)
def clean_db(container):
    """Clean specific tables before and after tests."""
    # We don't want to wipe the whole DB if it's the dev DB, 
    # but for this test we'll clean up our specific test artifacts
    def _cleanup():
        with container._database.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM reports WHERE report_type = 'test_integration'")
                cur.execute("DELETE FROM articles WHERE title LIKE 'Integration Test%'")
    
    _cleanup()
    yield
    _cleanup()


@patch("src.adapters.rss_parser.FeedparserRSSParser.parse")
@patch("src.adapters.gemini_client.GeminiLLMClient.summarize")
@patch("src.adapters.gemini_client.GeminiLLMClient.extract_keywords")
@patch("src.adapters.gemini_client.GeminiLLMClient.generate_digest")
@patch("src.adapters.telegram_sender.httpx.post")
def test_full_pipeline_end_to_end(
    mock_telegram_post,
    mock_generate_digest,
    mock_extract_keywords,
    mock_summarize,
    mock_parse_rss,
    container,
):
    """
    Tests the complete flow:
    1. Crawl feeds (mocked RSS)
    2. Analyze articles (mocked LLM)
    3. Generate report (mocked LLM)
    4. Send report (mocked Telegram)
    
    Verifies that state is correctly persisted to the database at each step.
    """
    
    # --- SETUP MOCKS ---
    
    # 1. Mock RSS feed parsing
    test_link = f"https://example.com/integration-test-{int(datetime.now().timestamp())}"
    mock_articles = [
        Article(
            title="Integration Test Article 1",
            link=test_link,
            source="Test Source",
            published_at=datetime.now(JST),
            content="This is test content for integration.",
        )
    ]
    # Return these articles only on the first call
    mock_parse_rss.side_effect = [mock_articles, [], []]
    
    # 2. Mock LLM Analysis
    mock_summarize.return_value = "Integration test summary."
    mock_extract_keywords.return_value = ["integration", "test"]
    
    # 3. Mock Report Generation
    mock_generate_digest.return_value = "Integration test digest."
    
    # 4. Mock Telegram
    mock_telegram_response = MagicMock()
    mock_telegram_response.status_code = 200
    mock_telegram_post.return_value = mock_telegram_response


    # --- EXECUTE PIPELINE ---
    
    # Step 1: Crawl
    crawl_uc = container.crawl_feeds_use_case()
    new_articles_count = crawl_uc.execute()
    
    assert new_articles_count >= 1, "Should have saved at least 1 new article"
    
    # Verify article is in DB but unprocessed
    with container._database.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT is_processed, summary FROM articles WHERE link = %s", (test_link,))
            row = cur.fetchone()
            assert row is not None, "Article wasn't saved to DB"
            assert row["is_processed"] is False
            assert row["summary"] == ""


    # Step 2: Analyze
    analyze_uc = container.analyze_articles_use_case()
    analyzed_count = analyze_uc.execute()
    
    assert analyzed_count >= 1, "Should have analyzed at least 1 article"
    
    # Verify article is now processed in DB
    with container._database.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT is_processed, summary, keywords FROM articles WHERE link = %s", (test_link,))
            row = cur.fetchone()
            assert row["is_processed"] is True
            assert row["summary"] == "Integration test summary."
            assert ["integration", "test"] == row["keywords"]


    # Step 3: Generate Report
    report_uc = container.generate_report_use_case()
    
    # Generate the report (we use a custom type to easily clean it up)
    success = report_uc.execute(report_type="test_integration")
    
    assert success is True, "Report generation should succeed"
    
    # Verify report was saved to DB
    with container._database.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT content FROM reports WHERE report_type = 'test_integration' ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            assert row is not None, "Report wasn't saved to DB"
            assert "Integration test digest." in row["content"]
            
    # Verify Telegram was called with the formatted report
    mock_telegram_post.assert_called_once()
    telegram_payload = mock_telegram_post.call_args[1]["json"]
    assert "Integration test digest." in telegram_payload["text"]
    assert "test_integration" in telegram_payload["text"] or "KAI-FINA" in telegram_payload["text"]
