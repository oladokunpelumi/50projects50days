from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return False


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    x_bearer_token: str = os.getenv("X_BEARER_TOKEN", "")
    x_api_base_url: str = os.getenv("X_API_BASE_URL", "https://api.x.com/2")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/twitter_agent.db")
    simulation_mode: bool = os.getenv("SIMULATION_MODE", "true").lower() == "true"
    default_keywords: List[str] = field(
        default_factory=lambda: [
            kw.strip().lower()
            for kw in os.getenv(
                "DEFAULT_KEYWORDS", "btc,bitcoin,eth,ethereum,solana,crypto,defi"
            ).split(",")
            if kw.strip()
        ]
    )
    default_hashtags: List[str] = field(
        default_factory=lambda: [
            tag.strip().lower()
            for tag in os.getenv(
                "DEFAULT_HASHTAGS", "#btc,#eth,#sol,#crypto,#defi"
            ).split(",")
            if tag.strip()
        ]
    )


settings = Settings()
