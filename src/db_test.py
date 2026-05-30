import psycopg2
import json
import os
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

def get_connection():
    raw_url = os.environ["POSTGRES_URL"]
    parsed = urlparse(raw_url)
    params = {k: v[0] for k, v in parse_qs(parsed.query).items() if k != 'channel_binding'}
    url = urlunparse(parsed._replace(query=urlencode(params)))
    return psycopg2.connect(url)

new_article = {
    "title": "Bitcoin ETF Inflows Hit Record High",
    "content": "Spot Bitcoin ETFs recorded their highest single-day inflows, signaling strong institutional demand.",
    "url": "https://example.com/btc-etf-record-3",
    "published_date": datetime.now(),
    "source": "CryptoNews",
    "sentiment_score": 0.85,
    "crypto_mentioned": json.dumps(["bitcoin"]),
}

conn = get_connection()
cur = conn.cursor()

cur.execute("""
    INSERT INTO articles (title, content, url, published_date, source, sentiment_score, crypto_mentioned)
    VALUES (%(title)s, %(content)s, %(url)s, %(published_date)s, %(source)s, %(sentiment_score)s, %(crypto_mentioned)s)
    ON CONFLICT (url) DO NOTHING
    RETURNING id
""", new_article)

row = cur.fetchone()
conn.commit()
cur.close()
conn.close()

if row:
    print(f"Inserted article with id={row[0]}")
else:
    print("Article already exists (url conflict), skipped.")
