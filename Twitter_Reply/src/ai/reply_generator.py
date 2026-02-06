from __future__ import annotations

import re

from openai import OpenAI

from config.personas import PERSONAS, select_persona
from config.settings import settings
from src.database.models import GeneratedReply, SessionLocal, Tweet


class ReplyGenerator:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def generate_reply(self, tweet: Tweet, persona_override: str | None = None) -> GeneratedReply:
        persona_key = select_persona(tweet.text, override=persona_override)
        persona = PERSONAS[persona_key]

        if self.client:
            content = self._openai_reply(tweet.text, persona["system_prompt"])
        else:
            content = self._fallback_reply(tweet.text, persona_key)

        cleaned = self._clean(content)

        with SessionLocal() as session:
            reply = GeneratedReply(tweet_id=tweet.id, persona=persona_key, reply_text=cleaned)
            session.add(reply)
            tweet.lifecycle_status = "reply_generated"
            session.merge(tweet)
            session.commit()
            session.refresh(reply)
            return reply

    def _openai_reply(self, tweet_text: str, system_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Draft one reply under 280 characters for this tweet. "
                        "No hashtags unless absolutely needed.\n\n"
                        f"Tweet: {tweet_text}"
                    ),
                },
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content or ""

    def _fallback_reply(self, tweet_text: str, persona_key: str) -> str:
        base = {
            "professional_analyst": "Useful angle: monitor liquidity, positioning, and downside risk before drawing conclusions.",
            "casual_degen": "Low-key interesting setup 👀 worth tracking on-chain before anyone gets too loud. NFA.",
            "neutral_researcher": "Interesting claim. Which dataset and timeframe support this conclusion?",
        }
        return f"{base[persona_key]} ({tweet_text[:80]})"

    def _clean(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text.strip())
        if len(text) > 280:
            text = text[:277].rstrip() + "..."
        return text
