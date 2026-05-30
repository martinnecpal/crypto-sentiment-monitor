import json
import logging
import os
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

POSTGRES_URL = os.environ.get('POSTGRES_URL')


class DatabaseManager:
    def __init__(self, db_path: str = "crypto_sentiment.db"):
        self.db_path = db_path
        self.use_postgres = bool(POSTGRES_URL)
        self.ph = "%s" if self.use_postgres else "?"
        self.init_database()
        logging.info(f"Database initialized ({'Postgres' if self.use_postgres else 'SQLite'})")

    def _connect(self):
        if self.use_postgres:
            import psycopg2
            from urllib.parse import urlparse, urlencode, urlunparse, parse_qs
            parsed = urlparse(POSTGRES_URL)
            params = {k: v[0] for k, v in parse_qs(parsed.query).items()
                      if k != 'channel_binding'}
            url = urlunparse(parsed._replace(query=urlencode(params)))
            return psycopg2.connect(url)
        else:
            import sqlite3
            return sqlite3.connect(self.db_path)

    def init_database(self):
        conn = self._connect()
        cursor = conn.cursor()

        if self.use_postgres:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT UNIQUE,
                    published_date TIMESTAMP,
                    source TEXT,
                    sentiment_score REAL,
                    crypto_mentioned TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT UNIQUE,
                    published_date DATETIME,
                    source TEXT,
                    sentiment_score REAL,
                    crypto_mentioned TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(published_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_crypto ON articles(crypto_mentioned)')
        conn.commit()
        conn.close()

    def insert_article(self, article):
        conn = self._connect()
        cursor = conn.cursor()
        ph = self.ph

        try:
            values = (
                article.title, article.content, article.url,
                article.published_date, article.source,
                article.sentiment_score,
                json.dumps(article.crypto_mentioned) if article.crypto_mentioned else None
            )
            if self.use_postgres:
                cursor.execute(f'''
                    INSERT INTO articles
                    (title, content, url, published_date, source, sentiment_score, crypto_mentioned)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                    ON CONFLICT (url) DO NOTHING
                ''', values)
            else:
                cursor.execute(f'''
                    INSERT OR IGNORE INTO articles
                    (title, content, url, published_date, source, sentiment_score, crypto_mentioned)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
                ''', values)
            conn.commit()
            logging.info(f"Inserted article: {article.title[:50]}...")
        except Exception as e:
            logging.error(f"Error inserting article: {e}")
        finally:
            conn.close()

    def get_sentiment_summary(self, days: int = 7) -> Dict:
        conn = self._connect()
        cursor = conn.cursor()
        ph = self.ph

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        cursor.execute(f'''
            SELECT crypto_mentioned, sentiment_score
            FROM articles
            WHERE published_date >= {ph} AND published_date <= {ph}
            AND crypto_mentioned IS NOT NULL
        ''', (start_date, end_date))

        results = cursor.fetchall()
        conn.close()

        summary = defaultdict(list)
        for crypto_json, sentiment in results:
            try:
                for crypto in json.loads(crypto_json):
                    summary[crypto].append(sentiment)
            except (json.JSONDecodeError, TypeError):
                continue

        final_summary = {}
        for crypto, sentiments in summary.items():
            if sentiments:
                final_summary[crypto] = {
                    'avg_sentiment': statistics.mean(sentiments),
                    'article_count': len(sentiments),
                    'positive_count': len([s for s in sentiments if s > 0.1]),
                    'negative_count': len([s for s in sentiments if s < -0.1]),
                    'neutral_count': len([s for s in sentiments if -0.1 <= s <= 0.1]),
                    'max_sentiment': max(sentiments),
                    'min_sentiment': min(sentiments)
                }

        return final_summary

    def get_todays_articles(self, limit: int = 50) -> list:
        conn = self._connect()
        cursor = conn.cursor()
        if self.use_postgres:
            cursor.execute(f'''
                SELECT title, source, sentiment_score, crypto_mentioned, published_date, url
                FROM articles
                WHERE published_date::date = CURRENT_DATE
                ORDER BY published_date DESC
                LIMIT {limit}
            ''')
        else:
            cursor.execute(f'''
                SELECT title, source, sentiment_score, crypto_mentioned, published_date, url
                FROM articles
                WHERE DATE(published_date) = DATE('now')
                ORDER BY published_date DESC
                LIMIT {limit}
            ''')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_article_count(self) -> int:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM articles')
        count = cursor.fetchone()[0]
        conn.close()
        return count
