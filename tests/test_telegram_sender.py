"""Unit tests for TelegramNotificationSender."""

from unittest.mock import patch, MagicMock

from src.adapters.telegram_sender import (
    ConsoleNotificationSender,
    TelegramNotificationSender,
)


class TestTelegramNotificationSender:
    """Tests for TelegramNotificationSender."""

    def setup_method(self):
        self.sender = TelegramNotificationSender(
            bot_token="fake_token_123",
            chat_id="999888777",
        )

    @patch("src.adapters.telegram_sender.httpx.post")
    def test_sends_message_successfully(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.sender.send("Hello from test")

        assert result is True
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        assert call_kwargs[1]["json"]["chat_id"] == "999888777"
        assert call_kwargs[1]["json"]["text"] == "Hello from test"

    @patch("src.adapters.telegram_sender.httpx.post")
    def test_returns_false_on_api_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_post.return_value = mock_response

        result = self.sender.send("test message")

        assert result is False

    @patch("src.adapters.telegram_sender.httpx.post")
    def test_splits_long_messages(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Create a message longer than 4096 chars
        long_msg = "Line of text\n" * 500  # ~6500 chars

        result = self.sender.send(long_msg)

        assert result is True
        assert mock_post.call_count >= 2  # Should be split into at least 2 chunks

    @patch("src.adapters.telegram_sender.httpx.post")
    def test_handles_http_exception(self, mock_post):
        import httpx
        mock_post.side_effect = httpx.HTTPError("Connection failed")

        result = self.sender.send("test")

        assert result is False

    def test_split_message_short(self):
        chunks = self.sender._split_message("Short message")
        assert len(chunks) == 1
        assert chunks[0] == "Short message"

    def test_split_message_at_newline(self):
        # Message just over limit, should split at last newline before limit
        line = "A" * 100 + "\n"
        msg = line * 50  # 5050 chars, over 4096
        chunks = self.sender._split_message(msg)
        assert len(chunks) >= 2
        # First chunk should end at a newline boundary
        assert len(chunks[0]) <= 4096


class TestConsoleNotificationSender:
    """Tests for ConsoleNotificationSender."""

    def test_always_returns_true(self):
        sender = ConsoleNotificationSender()
        result = sender.send("Test console message")
        assert result is True
