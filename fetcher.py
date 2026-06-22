import csv
import feedparser
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from HeadlineDeduplicator import HeadlineDeduplicator

FETCH_TIMEOUT = 15  # seconds per feed

# Add new feed sources here
FEEDS = [
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "source": "CoinDesk"},
    {"url": "https://cointelegraph.com/rss", "source": "Cointelegraph"},
    {"url": "https://cryptoslate.com/feed/", "source": "CryptoSlate"},
    {"url": "https://cryptopotato.com/feed/","source": "CryptoPotato"},
    {"url": "https://cryptonews.com/news/feed/", "source":"CryptoNews"},
    {"url": "https://thedefiant.io/feed/", "source":"The Defiant"},
    {"url": "https://tokeninsight.com/rss/news", "source":"TokenInsight"},
]

_HEADERS = {"User-Agent": "crypto-sentiment-monitor/1.0"}


def _parse_time(entry):
    if hasattr(entry, "published"):
        try:
            dt = parsedate_to_datetime(entry.published)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return None
    return None


def fetch_feed(feed_config: dict, cutoff_hours: int = 6) -> list[dict]:
    try:
        resp = requests.get(feed_config["url"], headers=_HEADERS, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"[{feed_config['source']}] skipped: {e}")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=cutoff_hours)
    articles = []

    for entry in feed.entries:
        published_at = _parse_time(entry)
        if published_at and published_at < cutoff:
            continue

        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue

        articles.append({
            "source": feed_config["source"],
            "title": title,
            "link": link,
            "published_at": published_at.isoformat() if published_at else None,
            "summary": entry.get("summary", "").strip(),
        })

    return articles


def fetch_all(cutoff_hours: int = 6) -> list[dict]:
    articles = []
    with ThreadPoolExecutor(max_workers=len(FEEDS)) as executor:
        futures = {executor.submit(fetch_feed, feed, cutoff_hours): feed for feed in FEEDS}
        for future in as_completed(futures):
            articles.extend(future.result())
    return articles


_CSV_FIELDS = ["source", "title", "link", "published_at", "fetched_at", "summary"]


def save_to_csv(articles: list[dict], path: str = "articles_test.csv") -> None:
    fetched_at = datetime.now(timezone.utc).isoformat()
    rows = [{**a, "fetched_at": fetched_at} for a in articles]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_from_csv(path: str = "articles_test.csv") -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    from store import store_articles
    articles = fetch_all()

    deduplicator = HeadlineDeduplicator()
    articles, removed = deduplicator.extract_titles(articles)

    articles = deduplicator.dedupe_titles_with_AI(articles)

    #save_to_csv(articles=articles,path='test.csv')

    inserted = store_articles(articles)
    print(f"Inserted {inserted} new articles from {len(FEEDS)} feed(s).")
    #print(articles)
