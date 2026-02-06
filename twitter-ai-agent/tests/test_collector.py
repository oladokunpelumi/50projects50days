from src.collectors.manual_import import extract_tweet_id
from src.collectors.twitter_client import TwitterClient


def test_simulated_tweet_collection_count():
    client = TwitterClient()
    tweets = client.generate_simulated_tweets(5)
    assert len(tweets) == 5
    assert all("tweet_id" in row and "text" in row for row in tweets)


def test_extract_tweet_id_from_url():
    tweet_id = extract_tweet_id("https://x.com/someone/status/1876543212345678901")
    assert tweet_id == "1876543212345678901"


def test_extract_tweet_id_from_raw_id():
    assert extract_tweet_id("1234567890123") == "1234567890123"
