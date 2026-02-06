from __future__ import annotations

import random
from datetime import datetime
from typing import Any

try:
    import requests
except ModuleNotFoundError:  # pragma: no cover
    requests = None

from config.settings import settings
from src.collectors.manual_import import extract_tweet_id


class TwitterClient:
    def __init__(self) -> None:
        self.base_url = settings.x_api_base_url
        self.bearer = settings.x_bearer_token
        self.simulation_mode = settings.simulation_mode or not self.bearer or requests is None

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.bearer}"}

    def get_tweet_by_id(self, tweet_id: str) -> dict[str, Any]:
        if self.simulation_mode:
            return self._simulate_single(tweet_id)

        url = f"{self.base_url}/tweets/{tweet_id}"
        params = {"tweet.fields": "public_metrics,created_at,author_id,text"}
        response = requests.get(url, headers=self._headers(), params=params, timeout=12)

        if response.status_code in {401, 403, 429}:
            self.simulation_mode = True
            return self._simulate_single(tweet_id)
        response.raise_for_status()
        data = response.json().get("data", {})
        metrics = data.get("public_metrics", {})
        return {
            "tweet_id": data.get("id", tweet_id),
            "text": data.get("text", ""),
            "author_handle": data.get("author_id", "unknown"),
            "source": "api",
            "imported_at": datetime.utcnow(),
            "like_count": metrics.get("like_count", 0),
            "retweet_count": metrics.get("retweet_count", 0),
            "reply_count": metrics.get("reply_count", 0),
        }

    def import_by_url_or_id(self, raw: str) -> dict[str, Any]:
        tweet_id = extract_tweet_id(raw)
        return self.get_tweet_by_id(tweet_id)

    def collect_from_list(self, list_id: str, max_results: int = 10) -> list[dict[str, Any]]:
        if self.simulation_mode:
            return self.generate_simulated_tweets(max_results)

        # Free tier often lacks list timeline; we degrade gracefully.
        url = f"{self.base_url}/lists/{list_id}/tweets"
        params = {"max_results": min(max_results, 100), "tweet.fields": "public_metrics,author_id,text"}
        response = requests.get(url, headers=self._headers(), params=params, timeout=12)
        if response.status_code in {401, 403, 404, 429}:
            self.simulation_mode = True
            return self.generate_simulated_tweets(max_results)
        response.raise_for_status()
        rows = []
        for item in response.json().get("data", []):
            metrics = item.get("public_metrics", {})
            rows.append(
                {
                    "tweet_id": item.get("id"),
                    "text": item.get("text", ""),
                    "author_handle": item.get("author_id", "unknown"),
                    "source": "api",
                    "imported_at": datetime.utcnow(),
                    "like_count": metrics.get("like_count", 0),
                    "retweet_count": metrics.get("retweet_count", 0),
                    "reply_count": metrics.get("reply_count", 0),
                }
            )
        return rows

    def generate_simulated_tweets(self, count: int = 10) -> list[dict[str, Any]]:
        templates = [
            "BTC liquidity is rotating into ETH L2s. Any data on stablecoin inflows?",
            "GM degens, SOL memes printing again but on-chain fees are rising.",
            "New paper compares DeFi risk models across lending protocols.",
            "Macro watch: rate cut odds changed. Crypto beta might react fast.",
            "Airdrop hunters piling into points farms. What's sustainable here?",
        ]
        items: list[dict[str, Any]] = []
        for _ in range(count):
            tweet_id = str(random.randint(10**12, 10**13 - 1))
            text = random.choice(templates)
            items.append(self._simulate_single(tweet_id, text))
        return items

    def _simulate_single(self, tweet_id: str, text: str | None = None) -> dict[str, Any]:
        if text is None:
            text = f"Simulated tweet {tweet_id} about crypto market structure and risk."
        return {
            "tweet_id": tweet_id,
            "text": text,
            "author_handle": f"sim_user_{tweet_id[-4:]}",
            "source": "simulation",
            "imported_at": datetime.utcnow(),
            "like_count": random.randint(0, 220),
            "retweet_count": random.randint(0, 80),
            "reply_count": random.randint(0, 40),
        }
