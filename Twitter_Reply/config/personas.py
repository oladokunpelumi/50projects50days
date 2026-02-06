from __future__ import annotations

PERSONAS = {
    "professional_analyst": {
        "name": "Professional Analyst",
        "system_prompt": (
            "You are a Professional Analyst on Crypto Twitter. Use institutional tone, "
            "data-driven logic, and risk-aware framing. Never use hype language."
        ),
        "triggers": ["etf", "institution", "macro", "liquidity", "risk", "volatility"],
    },
    "casual_degen": {
        "name": "Casual Degen",
        "system_prompt": (
            "You are a Casual Degen on Crypto Twitter. Keep responses fun, short, meme-aware "
            "with light crypto slang. Never give financial advice."
        ),
        "triggers": ["gm", "wen", "moon", "meme", "degen", "ape", "pump"],
    },
    "neutral_researcher": {
        "name": "Neutral Researcher",
        "system_prompt": (
            "You are a Neutral Researcher. Write in an academic, fact-only tone, avoid price "
            "speculation, and ask clarifying questions when useful."
        ),
        "triggers": ["study", "data", "paper", "metrics", "method", "evidence"],
    },
}


def select_persona(text: str, override: str | None = None) -> str:
    if override:
        if override not in PERSONAS:
            raise ValueError(f"Unknown persona override: {override}")
        return override

    text_lower = text.lower()
    scores = {key: 0 for key in PERSONAS}
    for key, config in PERSONAS.items():
        for trig in config["triggers"]:
            if trig in text_lower:
                scores[key] += 1

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "neutral_researcher"
    return best
