from src.filters.keyword_filter import evaluate_relevance


def test_keyword_filter_case_insensitive_matching():
    result = evaluate_relevance(
        "BTC liquidity and #DeFi adoption are rising",
        keywords=["bitcoin", "liquidity"],
        hashtags=["#defi"],
    )
    assert result.matched is True
    assert "liquidity" in result.matches
    assert "#defi" in result.matches
    assert result.relevance_score > 0
