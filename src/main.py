# src/main.py
import requests
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict
import re
from textblob import TextBlob
from database import DatabaseManager

@dataclass
class Article:
    title: str
    content: str
    url: str
    published_date: datetime
    source: str
    sentiment_score: float = 0.0
    crypto_mentioned: List[str] = None

class NewsMonitor:
    """Monitors cryptocurrency news and analyzes sentiment"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'dogecoin', 'doge',
            'cardano', 'ada', 'solana', 'sol', 'polkadot', 'dot',
            'chainlink', 'link', 'litecoin', 'ltc', 'polygon', 'matic',
            'avalanche', 'avax', 'uniswap', 'uni'
        ]
        
    def fetch_crypto_news(self) -> List[Article]:
        """Fetch news articles - simplified version using NewsAPI"""
        articles = []
        
        # Sample articles for demo (replace with real API calls)
        sample_articles = [
            {
                'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                'content': 'Bitcoin continues to surge as more institutions embrace cryptocurrency. The positive market sentiment reflects growing confidence in digital assets.',
                'url': 'https://example.com/bitcoin-ath',
                'source': 'CryptoNews',
                'publishedAt': datetime.now().isoformat()
            },
            {
                'title': 'Ethereum Network Upgrade Causes Mixed Market Reactions',
                'content': 'The latest Ethereum upgrade has received mixed reactions from investors. While some are optimistic, others express concerns about potential issues.',
                'url': 'https://example.com/ethereum-upgrade',
                'source': 'BlockchainDaily',
                'publishedAt': datetime.now().isoformat()
            },
            {
                'title': 'Regulatory Concerns Impact Cryptocurrency Market Sentiment',
                'content': 'New regulatory announcements have caused uncertainty in the crypto market. Investors are showing bearish sentiment amid unclear regulations.',
                'url': 'https://example.com/regulatory-concerns',
                'source': 'FinanceToday',
                'publishedAt': datetime.now().isoformat()
            }
        ]
        
        for article_data in sample_articles:
            try:
                article = Article(
                    title=article_data['title'],
                    content=article_data['content'],
                    url=article_data['url'],
                    published_date=datetime.fromisoformat(article_data['publishedAt'].replace('Z', '+00:00')),
                    source=article_data['source']
                )
                
                # Analyze sentiment
                article.sentiment_score = self.analyze_sentiment(article.content)
                article.crypto_mentioned = self.identify_cryptos(article.title + ' ' + article.content)
                
                articles.append(article)
                
            except Exception as e:
                logging.error(f"Error processing article: {e}")
                continue
                
        return articles
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity  # Returns value between -1 and 1
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            return 0.0
    
    def identify_cryptos(self, text: str) -> List[str]:
        """Identify mentioned cryptocurrencies in text"""
        text_lower = text.lower()
        mentioned = []
        
        for crypto in self.crypto_keywords:
            if re.search(r'\b' + crypto + r'\b', text_lower):
                # Normalize to common names
                if crypto in ['btc']:
                    mentioned.append('bitcoin')
                elif crypto in ['eth']:
                    mentioned.append('ethereum')
                elif crypto in ['doge']:
                    mentioned.append('dogecoin')
                else:
                    mentioned.append(crypto)
        
        return list(set(mentioned))  # Remove duplicates
    
    def monitor_news(self):
        """Main monitoring function"""
        logging.info("Starting news monitoring...")
        
        # Fetch articles
        articles = self.fetch_crypto_news()
        logging.info(f"Fetched {len(articles)} articles")
        
        # Store articles
        for article in articles:
            self.db.insert_article(article)
        
        logging.info("News monitoring completed")
    
    def get_market_sentiment_report(self) -> str:
        """Generate a human-readable market sentiment report"""
        summary = self.db.get_sentiment_summary(days=7)
        
        if not summary:
            return "No sentiment data available."
        
        report = []
        report.append("CRYPTO MARKET SENTIMENT ANALYSIS")
        report.append("=" * 40)
        report.append("")
        
        # Sort by sentiment score
        sorted_cryptos = sorted(summary.items(), key=lambda x: x[1]['avg_sentiment'], reverse=True)
        
        for crypto, data in sorted_cryptos:
            sentiment_label = "BULLISH" if data['avg_sentiment'] > 0.1 else "BEARISH" if data['avg_sentiment'] < -0.1 else "NEUTRAL"
            
            report.append(f"{crypto.upper()}: {sentiment_label}")
            report.append(f"  Average Sentiment: {data['avg_sentiment']:.3f}")
            report.append(f"  Articles Analyzed: {data['article_count']}")
            report.append(f"  Positive: {data['positive_count']} | Negative: {data['negative_count']} | Neutral: {data['neutral_count']}")
            report.append("")
        
        return "\n".join(report)