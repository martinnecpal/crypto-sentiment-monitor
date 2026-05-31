import psycopg2
import json
import os
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs

# Load .env.local when running locally (not available in CI — POSTGRES_URL injected via env secret)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))
except ImportError:
    pass

def get_connection():
    raw_url = os.environ["POSTGRES_URL"]
    parsed = urlparse(raw_url)
    params = {k: v[0] for k, v in parse_qs(parsed.query).items() if k != 'channel_binding'}
    url = urlunparse(parsed._replace(query=urlencode(params)))
    return psycopg2.connect(url)

ts = datetime.now().strftime("%Y%m%d%H%M%S")

test_article = {
    "title": f"[DB TEST] Bitcoin ETF Inflows Hit Record High",
    "content": "Spot Bitcoin ETFs recorded their highest single-day inflows, signaling strong institutional demand.",
    "url": f"https://example.com/db-test-{ts}",
    "published_date": datetime.now(),
    "source": "db_test",
    "sentiment_score": 0.85,
    "crypto_mentioned": json.dumps(["bitcoin"]),
}

conn = get_connection()
cur = conn.cursor()

try:
    cur.execute("""
        INSERT INTO articles (title, content, url, published_date, source, sentiment_score, crypto_mentioned)
        VALUES (%(title)s, %(content)s, %(url)s, %(published_date)s, %(source)s, %(sentiment_score)s, %(crypto_mentioned)s)
        RETURNING id
    """, test_article)
    new_id = cur.fetchone()[0]
    conn.commit()
    print(f"INSERT ok — id={new_id}")

    #cur.execute("DELETE FROM articles WHERE id = %s", (new_id,))
    #conn.commit()
    #print(f"DELETE ok — id={new_id}")

    #print("Database connectivity test passed.")
finally:
    cur.close()
    conn.close()
