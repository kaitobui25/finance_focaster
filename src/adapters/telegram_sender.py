"""Notification sender adapters.

Implements NotificationSender interface for Telegram and Console output.
"""

from __future__ import annotations

import logging

import httpx

from src.domain.interfaces.repositories import NotificationSender

logger = logging.getLogger(__name__)


class TelegramNotificationSender(NotificationSender):
    """Send notifications via Telegram Bot API."""

    TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
    MAX_MESSAGE_LENGTH = 4096  # Telegram limit

    def __init__(self, bot_token: str, chat_id: str) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._url = self.TELEGRAM_API_URL.format(token=bot_token)

    def send(self, message: str) -> bool:
        """Send a message via Telegram."""
        try:
            # Split long messages
            chunks = self._split_message(message)
            for chunk in chunks:
                response = httpx.post(
                    self._url,
                    json={
                        "chat_id": self._chat_id,
                        "text": chunk,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                    timeout=30,
                )

                if response.status_code != 200:
                    logger.error(
                        "Telegram API error: %s - %s",
                        response.status_code,
                        response.text,
                    )
                    return False

            logger.info("Telegram message sent successfully (%d chunks)", len(chunks))
            return True

        except httpx.HTTPError as exc:
            logger.error("Telegram HTTP error: %s", exc)
            return False

    def _split_message(self, message: str) -> list[str]:
        """Split message into chunks that fit Telegram's limit."""
        if len(message) <= self.MAX_MESSAGE_LENGTH:
            return [message]

        chunks = []
        while message:
            if len(message) <= self.MAX_MESSAGE_LENGTH:
                chunks.append(message)
                break

            # Find a good split point (newline)
            split_point = message.rfind("\n", 0, self.MAX_MESSAGE_LENGTH)
            if split_point == -1:
                split_point = self.MAX_MESSAGE_LENGTH

            chunks.append(message[:split_point])
            message = message[split_point:].lstrip("\n")

        return chunks


class ConsoleNotificationSender(NotificationSender):
    """Fallback sender that prints to console/log."""

    def send(self, message: str) -> bool:
        """Print message to console."""
        separator = "=" * 60
        logger.info("\n%s\n📬 REPORT OUTPUT\n%s\n%s\n%s", separator, separator, message, separator)
        return True
