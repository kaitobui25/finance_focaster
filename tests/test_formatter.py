"""Unit tests for ReportFormatter."""

from datetime import datetime, timezone, timedelta

from src.adapters.message_formatter import DISCLAIMER, SEPARATOR, ReportFormatter

# Fixed JST datetime for deterministic testing
JST = timezone(timedelta(hours=9))
FIXED_NOW = datetime(2026, 3, 1, 16, 30, 0, tzinfo=JST)


class TestReportFormatter:
    """Tests for ReportFormatter."""

    def setup_method(self):
        self.formatter = ReportFormatter()

    def test_morning_report_has_correct_header(self):
        result = self.formatter.format("morning", FIXED_NOW, "test content")
        assert "🌅 KAI-FINA | Pre-Market Brief" in result
        assert "📅 2026-03-01" in result
        assert "⏰ 16:30 JST" in result

    def test_evening_report_has_correct_header(self):
        result = self.formatter.format("evening", FIXED_NOW, "test content")
        assert "🌙 KAI-FINA | End-of-Day Report" in result
        assert "📅 2026-03-01" in result
        assert "Phiên giao dịch Tokyo đã đóng cửa" in result

    def test_report_contains_llm_content(self):
        content = "📊 KẾT QUẢ PHIÊN\n• Nikkei 225: 40,000"
        result = self.formatter.format("evening", FIXED_NOW, content)
        assert content in result

    def test_report_contains_disclaimer(self):
        result = self.formatter.format("evening", FIXED_NOW, "test")
        assert "⚠️ DISCLAIMER" in result
        assert "không phải tư vấn tài chính" in result

    def test_report_contains_separator(self):
        result = self.formatter.format("morning", FIXED_NOW, "test")
        assert SEPARATOR in result

    def test_morning_and_evening_headers_differ(self):
        morning = self.formatter.format("morning", FIXED_NOW, "same content")
        evening = self.formatter.format("evening", FIXED_NOW, "same content")
        assert "Pre-Market Brief" in morning
        assert "End-of-Day Report" in evening
        assert morning != evening

    def test_unknown_report_type_defaults_to_evening(self):
        result = self.formatter.format("unknown", FIXED_NOW, "test")
        assert "🌙 KAI-FINA | End-of-Day Report" in result
