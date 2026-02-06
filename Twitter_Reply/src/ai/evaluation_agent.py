from __future__ import annotations

import json

from openai import OpenAI

from config.settings import settings
from src.database.models import EvaluationResult, GeneratedReply, SessionLocal


class EvaluationAgent:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def evaluate_reply(self, reply: GeneratedReply) -> EvaluationResult:
        if self.client:
            result = self._openai_eval(reply.reply_text, reply.persona)
        else:
            result = self._fallback_eval(reply.reply_text, reply.persona)

        with SessionLocal() as session:
            db_reply = session.get(GeneratedReply, reply.id)
            evaluation = EvaluationResult(
                reply_id=reply.id,
                relevance_score=result["relevance"],
                tone_accuracy_score=result["tone_accuracy"],
                value_add_score=result["value_added"],
                engagement_potential_score=result["engagement_potential"],
                predicted_likes=result["predicted_likes"],
                predicted_retweets=result["predicted_retweets"],
                predicted_replies=result["predicted_replies"],
                raw_json=result,
            )
            db_reply.status = "evaluated"
            session.add(evaluation)
            session.commit()
            session.refresh(evaluation)
            return evaluation

    def _openai_eval(self, text: str, persona: str) -> dict:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Evaluate tweet reply quality. Return strict JSON with keys: "
                        "relevance, tone_accuracy, value_added, engagement_potential, "
                        "predicted_likes, predicted_retweets, predicted_replies. "
                        "Scores 0-1."
                    ),
                },
                {"role": "user", "content": f"Persona: {persona}\nReply: {text}"},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content or "{}")

    def _fallback_eval(self, text: str, persona: str) -> dict:
        length_factor = min(len(text) / 280, 1)
        base = 0.55 + 0.35 * length_factor
        persona_bonus = 0.05 if persona == "professional_analyst" else 0.0
        score = min(base + persona_bonus, 0.97)
        return {
            "relevance": round(score, 2),
            "tone_accuracy": round(score - 0.03, 2),
            "value_added": round(score - 0.06, 2),
            "engagement_potential": round(score - 0.02, 2),
            "predicted_likes": int(8 + 40 * score),
            "predicted_retweets": int(2 + 12 * score),
            "predicted_replies": int(1 + 9 * score),
        }
