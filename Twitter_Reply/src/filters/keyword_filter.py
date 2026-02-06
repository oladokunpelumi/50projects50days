from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FilterResult:
    matched: bool
    relevance_score: float
    matches: list[str]


def evaluate_relevance(text: str, keywords: list[str], hashtags: list[str]) -> FilterResult:
    haystack = text.lower()
    all_terms = [term.lower() for term in keywords + hashtags]
    matches = [term for term in all_terms if term in haystack]
    unique_matches = sorted(set(matches))
    denom = max(len(set(all_terms)), 1)
    score = min(len(unique_matches) / denom, 1.0)
    return FilterResult(matched=bool(unique_matches), relevance_score=score, matches=unique_matches)
