# src/database.py
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List
import statistics
from collections import defaultdict
import logging

class DatabaseManager:
    """Database manager optimized for GitHub Actions"""
    
    def __init__(self, db_path: str = "crypto_sentiment.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crypto_name TEXT,
                date DATE,
                avg_sentiment REAL,
                article_count INTEGER,
                positive_count INTEGER,
                negative_count INTEGER,
                neutral_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(published_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_articles_crypto ON articles(crypto_mentioned)
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully")
    
    def insert_article(self, article):
        """Insert a new article into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO articles 
                (title, content, url, published_date, source, sentiment_score, crypto_mentioned)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.title,
                article.content,
                article.url,
                article.published_date,
                article.source,
                article.sentiment_score,
                json.dumps(article.crypto_mentioned) if article.crypto_mentioned else None
            ))
            conn.commit()
            logging.info(f"Inserted article: {article.title[:50]}...")
        except sqlite3.IntegrityError:
            logging.debug(f"Article already exists: {article.url}")
        except Exception as e:
            logging.error(f"Error inserting article: {e}")
        finally:
            conn.close()
    
    def get_sentiment_summary(self, days: int = 7) -> Dict:
        """Get sentiment summary for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        cursor.execute('''
            SELECT crypto_mentioned, sentiment_score, published_date
            FROM articles
            WHERE published_date >= ? AND published_date <= ?
            AND crypto_mentioned IS NOT NULL
        ''', (start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()
        
        summary = defaultdict(list)
        for crypto_json, sentiment, date in results:
            if crypto_json:
                try:
                    cryptos = json.loads(crypto_json)
                    for crypto in cryptos:
                        summary[crypto].append(sentiment)
                except json.JSONDecodeError:
                    continue
        
        # Calculate statistics
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
    
    def get_article_count(self) -> int:
        """Get total number of articles in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM articles')
        count = cursor.fetchone()[0]
        conn.close()
        return count