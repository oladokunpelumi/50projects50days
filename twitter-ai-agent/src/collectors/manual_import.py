from __future__ import annotations

import re
from dataclasses import dataclass


TWEET_ID_REGEX = re.compile(r"(?:status/|statuses/|^)(\d{6,25})")


@dataclass
class ImportedTweet:
    tweet_id: str
    text: str
    author_handle: str = "manual_user"


def extract_tweet_id(url_or_id: str) -> str:
    candidate = url_or_id.strip()
    if candidate.isdigit():
        return candidate
    match = TWEET_ID_REGEX.search(candidate)
    if not match:
        raise ValueError(f"Unable to parse tweet ID from input: {url_or_id}")
    return match.group(1)
