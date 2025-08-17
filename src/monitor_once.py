# src/monitor_once.py
import json
import logging
import sqlite3
from datetime import datetime
from main import NewsMonitor, DatabaseManager
import os

# Configure logging for GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_sentiment.log'),
        logging.StreamHandler()
    ]
)

class GitHubActionsMonitor(NewsMonitor):
    """Modified monitor for GitHub Actions single runs"""
    
    def __init__(self):
        # Use in-memory database for GitHub Actions
        super().__init__()
        self.output_dir = "."
        
    def save_results_to_json(self):
        """Save monitoring results to JSON files for artifact upload"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get sentiment summary
        summary = self.db.get_sentiment_summary(days=1)  # Only today's data
        
        # Save summary
        summary_file = f"sentiment_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'summary': summary,
                'total_cryptos': len(summary)
            }, f, indent=2)
        
        # Get recent articles
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, source, sentiment_score, crypto_mentioned, published_date, url
            FROM articles
            WHERE DATE(published_date) = DATE('now')
            ORDER BY published_date DESC
            LIMIT 50
        ''')
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'title': row[0],
                'source': row[1],
                'sentiment_score': row[2],
                'crypto_mentioned': json.loads(row[3]) if row[3] else [],
                'published_date': row[4],
                'url': row[5]
            })
        
        conn.close()
        
        # Save articles
        articles_file = f"articles_{timestamp}.json"
        with open(articles_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'articles': articles,
                'total_articles': len(articles)
            }, f, indent=2)
        
        # Generate human-readable report
        report = self.get_market_sentiment_report()
        report_file = f"sentiment_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(f"Crypto Sentiment Report - {timestamp}\n")
            f.write("=" * 50 + "\n\n")
            f.write(report)
        
        logging.info(f"Results saved to: {summary_file}, {articles_file}, {report_file}")
        
        return {
            'summary_file': summary_file,
            'articles_file': articles_file,
            'report_file': report_file
        }

def main():
    """Main function for GitHub Actions"""
    logging.info("🚀 Starting crypto sentiment monitoring (GitHub Actions mode)")
    
    try:
        # Initialize monitor
        monitor = GitHubActionsMonitor()
        
        # Run monitoring
        logging.info("📰 Fetching and analyzing news...")
        monitor.monitor_news()
        
        # Save results
        logging.info("💾 Saving results...")
        files = monitor.save_results_to_json()
        
        # Print summary for GitHub Actions logs
        summary = monitor.db.get_sentiment_summary(days=1)
        
        print("\n" + "="*60)
        print("🎯 CRYPTO SENTIMENT SUMMARY")
        print("="*60)
        
        if summary:
            for crypto, data in sorted(summary.items(), key=lambda x: x[1]['avg_sentiment'], reverse=True):
                sentiment_emoji = "🟢" if data['avg_sentiment'] > 0.1 else "🔴" if data['avg_sentiment'] < -0.1 else "🟡"
                sentiment_label = "Bullish" if data['avg_sentiment'] > 0.1 else "Bearish" if data['avg_sentiment'] < -0.1 else "Neutral"
                
                print(f"{sentiment_emoji} {crypto.upper()}: {sentiment_label} ({data['avg_sentiment']:.3f})")
                print(f"   📊 Articles: {data['article_count']} | ✅ Positive: {data['positive_count']} | ❌ Negative: {data['negative_count']}")
        else:
            print("No sentiment data available for today")
        
        print("\n" + "="*60)
        print(f"📁 Files created: {', '.join(files.values())}")
        print("="*60)
        
        logging.info("✅ Monitoring completed successfully")
        
    except Exception as e:
        logging.error(f"❌ Error during monitoring: {e}")
        raise

if __name__ == "__main__":
    main()