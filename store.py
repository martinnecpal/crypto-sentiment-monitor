import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def store_articles(articles: list[dict]) -> int:
    if not articles:
        return 0
    client = get_client()
    fetched_at = datetime.now(timezone.utc).isoformat()
    rows = [{**article, "fetched_at": fetched_at} for article in articles]
    result = (
        client.table("news_raw")
        .upsert(rows, on_conflict="link", ignore_duplicates=True)
        .execute()
    )
    return len(result.data) if result.data else 0
