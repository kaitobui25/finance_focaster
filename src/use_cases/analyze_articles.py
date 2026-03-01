"""Use case: Analyze unprocessed articles using LLM."""

from __future__ import annotations

import logging

from src.domain.interfaces.repositories import ArticleRepository, LLMClient

logger = logging.getLogger(__name__)


class AnalyzeArticlesUseCase:
    """Analyze unprocessed articles: summarize and extract keywords via LLM."""

    def __init__(
        self,
        llm_client: LLMClient,
        article_repo: ArticleRepository,
    ) -> None:
        self._llm_client = llm_client
        self._article_repo = article_repo

    def execute(self) -> int:
        """Analyze all unprocessed articles. Returns count of analyzed articles."""
        articles = self._article_repo.find_unprocessed()

        if not articles:
            logger.info("No unprocessed articles to analyze")
            return 0

        logger.info("Analyzing %d unprocessed articles", len(articles))
        analyzed = 0

        for article in articles:
            try:
                # Build text for LLM (title + content)
                text = f"{article.title}\n\n{article.content}" if article.content else article.title

                # Summarize
                summary = self._llm_client.summarize(text, title=article.title)

                # Extract keywords
                keywords = self._llm_client.extract_keywords(text, title=article.title)

                # Update in database
                self._article_repo.mark_processed(article.id, summary, keywords)
                analyzed += 1

                logger.debug(
                    "Analyzed article %d: %s -> %d keywords",
                    article.id,
                    article.title[:50],
                    len(keywords),
                )

            except Exception as exc:
                logger.error(
                    "Error analyzing article %d (%s): %s",
                    article.id,
                    article.title[:50],
                    exc,
                )
                continue

        logger.info("Analysis complete: %d/%d articles analyzed", analyzed, len(articles))
        return analyzed
