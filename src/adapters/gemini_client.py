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

MORNING_DIGEST_PROMPT = """You are KAI-FINA, an AI agent specializing in Japanese financial market analysis.
Based on the following news articles, create a MORNING PRE-MARKET BRIEF.

You MUST output the content in EXACTLY this structure (use these exact emoji and section headers):

🌍 QUA ĐÊM (Wall St / Futures)
• S&P 500: [infer from articles or write [Không có dữ liệu]]
• Nasdaq: [infer from articles or write [Không có dữ liệu]]
• Nikkei Futures: [infer from articles or write [Không có dữ liệu]]
• USD/JPY: [infer from articles or write [Không có dữ liệu]]
• XAU/USD: [infer from articles or write [Không có dữ liệu]]

📰 TIN QUAN TRỌNG QUA ĐÊM
• [Top 3-5 important news, each in 1 line — extracted from articles]

🎯 ĐỊNH HƯỚNG HÔM NAY
Tâm lý thị trường: [Risk-ON / Risk-OFF / Trung lập] — based on your analysis
Nikkei dự kiến mở cửa: [Tăng/Giảm/Sideway] vì [brief reason]

⚡ CẦN CHÚ Ý HÔM NAY
• [Important events/data releases today if mentioned in articles]

⚠️ RỦI RO CẦN WATCH
• [Key risks to monitor]

Rules:
- Write in Vietnamese (mixed with English for financial terms).
- If data is not available in the articles, write [Không có dữ liệu].
- Be concise. Each bullet point should be 1 line max.
- Do NOT add any header or footer — only the sections above.

Articles:
{articles_text}

Morning Brief:"""

EVENING_DIGEST_PROMPT = """You are KAI-FINA, an AI agent specializing in Japanese financial market analysis.
Based on the following news articles, create an EVENING END-OF-DAY REPORT.

You MUST output the content in EXACTLY this structure (use these exact emoji and section headers):

📊 KẾT QUẢ PHIÊN
• Nikkei 225: [infer from articles or write [Không có dữ liệu]]
• TOPIX: [infer from articles or write [Không có dữ liệu]]
• USD/JPY: [infer from articles or write [Không có dữ liệu]]
• XAU/USD: [infer from articles or write [Không có dữ liệu]]

🏆 NGÀNH MẠNH NHẤT HÔM NAY
1. [Sector A]: [reason] — inferred from articles
2. [Sector B]: [reason]

📉 NGÀNH YẾU NHẤT HÔM NAY
1. [Sector X]: [reason]

━━━━━━━━━━━━━━━━━━━━━
🧠 PHÂN TÍCH SÂU

[Chính sách Vĩ mô]
→ [Policy news impact from articles]

[Dòng tiền]
→ [Foreign investor flow if mentioned, otherwise [Không có dữ liệu]]

[Dự phóng Lợi nhuận]
→ [Earnings-related news if any]

[Chu kỳ kinh tế / Sector Rotation]
→ [Current cycle assessment based on articles]

━━━━━━━━━━━━━━━━━━━━━
💡 KHUYẾN NGHỊ HÔM NAY

🟢 MUA / TÍCH LŨY
• [Asset/Sector/ETF] — [Reason based on which framework] — [Price zone if available]

🟡 THEO DÕI (Chưa vào lệnh)
• [Asset] — [Condition needed to enter]

🔴 TRÁNH / CẨN THẬN
• [Asset/Sector] — [Risk reason]

Rules:
- Write in Vietnamese (mixed with English for financial terms).
- If data is not available in the articles, write [Không có dữ liệu].
- Be concise. Each bullet point should be 1 line max.
- In PHÂN TÍCH SÂU, order the 4 frameworks by priority: Vĩ mô (#1) → Dòng tiền (#2) → Dự phóng Lợi nhuận (#3) → Chu kỳ (#4).
- In KHUYẾN NGHỊ, always state which framework supports the recommendation.
- Do NOT add any header or footer — only the sections above.

Articles:
{articles_text}

Evening Report:"""


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

    def generate_digest(self, articles_data: list[dict], report_type: str = "evening") -> str:
        """Generate a daily digest from analyzed articles.

        Args:
            articles_data: List of article dicts.
            report_type: "morning" or "evening".
        """
        articles_text = ""
        for i, article in enumerate(articles_data, 1):
            articles_text += (
                f"\n{i}. [{article.get('source', 'Unknown')}] "
                f"{article.get('title', 'No title')}\n"
                f"   Summary: {article.get('summary', 'No summary')}\n"
                f"   Keywords: {', '.join(article.get('keywords', []))}\n"
            )

        if report_type == "morning":
            prompt = MORNING_DIGEST_PROMPT.format(articles_text=articles_text)
        else:
            prompt = EVENING_DIGEST_PROMPT.format(articles_text=articles_text)

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
