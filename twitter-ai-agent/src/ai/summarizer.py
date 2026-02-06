from __future__ import annotations

import json
from collections import Counter

from openai import OpenAI

from config.settings import settings
from src.database.models import Tweet


class Summarizer:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def summarize(self, tweets: list[Tweet]) -> dict:
        if not tweets:
            return {
                "executive_summary": "No tweets in the selected period.",
                "sentiment": "neutral",
                "trends": [],
                "risks": [],
            }

        if self.client:
            return self._openai_summary(tweets)
        return self._fallback_summary(tweets)

    def _openai_summary(self, tweets: list[Tweet]) -> dict:
        lines = [f"- {t.text}" for t in tweets[:50]]
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return strict JSON with keys: executive_summary, sentiment, trends, risks. "
                        "No markdown, no extra keys."
                    ),
                },
                {"role": "user", "content": "Tweets:\n" + "\n".join(lines)},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    def _fallback_summary(self, tweets: list[Tweet]) -> dict:
        words = []
        for t in tweets:
            words.extend([w.strip(".,!?():;").lower() for w in t.text.split() if len(w) > 4])
        common = [w for w, _ in Counter(words).most_common(5)]
        return {
            "executive_summary": f"Analyzed {len(tweets)} tweets focused on crypto market narratives.",
            "sentiment": "mixed",
            "trends": common,
            "risks": ["Volatility spikes", "Narrative-driven overreaction"],
        }
