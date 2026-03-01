"""Gemini LLM client adapter.

Implements LLMClient interface using Google's new google-genai SDK.
"""

from __future__ import annotations

import json
import logging
import time

from google import genai
from google.genai.types import GenerateContentConfig

from src.domain.interfaces.repositories import LLMClient

logger = logging.getLogger(__name__)

# Prompt templates
SUMMARIZE_PROMPT = """You are a financial news analyst specializing in the Japanese market.
Summarize the following article in 2-3 concise sentences in English.
Focus on: market impact, key numbers, and actionable insights.
If relevant to Japan's market (Nikkei, TOPIX, JPY, BOJ), highlight that connection.

Article title: {title}
Article content: {content}

Summary:"""

KEYWORDS_PROMPT = """Extract 3-7 key financial/market keywords from this article.
Focus on: company names, market indices, economic indicators, policy terms, sectors.
Return ONLY a JSON array of strings, nothing else.

Example: ["BOJ", "interest rate", "Nikkei 225", "banking sector"]

Article title: {title}
Article content: {content}

Keywords:"""

DIGEST_PROMPT = """You are Antigravity, an AI agent specializing in Japanese financial market analysis.
Create a concise daily news digest from the following articles.

Group the news by theme (e.g., Japan Market, Global Markets, Geopolitics, Central Banks).
For each group:
- List the key headlines with 1-line summaries
- Highlight any connections to the Japanese market

At the end, add a brief "Market Implications" section noting the top 3 takeaways
for investors focused on Japan (stocks, XAU/USD, USD/JPY).

Articles:
{articles_text}

Daily Digest:"""


class GeminiLLMClient(LLMClient):
    """LLM client implementation using Google Gemini via google-genai SDK."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name
        self._retry_delay = 2
        self._max_retries = 3
        logger.info("Gemini LLM client initialized with model: %s", model_name)

    def summarize(self, text: str, title: str = "") -> str:
        """Summarize an article text."""
        prompt = SUMMARIZE_PROMPT.format(title=title, content=text[:3000])
        return self._generate(prompt)

    def extract_keywords(self, text: str, title: str = "") -> list[str]:
        """Extract keywords from article text."""
        prompt = KEYWORDS_PROMPT.format(title=title, content=text[:3000])
        response = self._generate(prompt)

        try:
            # Try to parse as JSON array
            keywords = json.loads(response)
            if isinstance(keywords, list):
                return [str(k).strip() for k in keywords if k]
        except json.JSONDecodeError:
            # Fallback: split by comma or newline
            keywords = [k.strip().strip('"').strip("'") for k in response.split(",")]
            return [k for k in keywords if k and len(k) > 1]

        return []

    def generate_digest(self, articles_data: list[dict]) -> str:
        """Generate a daily digest from analyzed articles."""
        articles_text = ""
        for i, article in enumerate(articles_data, 1):
            articles_text += (
                f"\n{i}. [{article.get('source', 'Unknown')}] "
                f"{article.get('title', 'No title')}\n"
                f"   Summary: {article.get('summary', 'No summary')}\n"
                f"   Keywords: {', '.join(article.get('keywords', []))}\n"
            )

        prompt = DIGEST_PROMPT.format(articles_text=articles_text)
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        """Call Gemini API with retry logic."""
        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                )
                return response.text.strip()
            except Exception as exc:
                logger.warning(
                    "Gemini API attempt %d/%d failed: %s",
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay * attempt)

        logger.error("Gemini API failed after %d attempts", self._max_retries)
        return "[LLM Error: Could not generate response]"
