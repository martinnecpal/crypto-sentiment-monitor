# Crypto Sentiment Monitor

Automated cryptocurrency news sentiment analysis that runs on GitHub Actions every 6 hours — no servers, no maintenance required.

## Features

- **Sentiment Analysis** — TextBlob NLP scores each article from -1 (bearish) to +1 (bullish)
- **Multi-Crypto Detection** — tracks 11 cryptocurrencies and their ticker aliases
- **Dual Database Support** — SQLite by default; Vercel Postgres when `POSTGRES_URL` secret is set
- **GitHub Actions** — fully automated, runs on schedule or on demand
- **Downloadable Reports** — JSON and text artifacts kept for 30 days

## Sentiment Thresholds

| Label | Score |
|---|---|
| Bullish | > 0.1 |
| Neutral | -0.1 to 0.1 |
| Bearish | < -0.1 |

## Supported Cryptocurrencies

Bitcoin (BTC), Ethereum (ETH), Dogecoin (DOGE), Cardano (ADA), Solana (SOL), Polkadot (DOT), Chainlink (LINK), Litecoin (LTC), Polygon (MATIC), Avalanche (AVAX), Uniswap (UNI)

Ticker aliases (e.g. `btc` → `bitcoin`) are normalized automatically.

## How It Works

Each run:
1. Fetches news articles via `fetch_crypto_news()` in `src/main.py`
2. Scores each article with TextBlob polarity
3. Detects which cryptos are mentioned (word-boundary regex)
4. Stores results in the database (duplicates skipped by unique URL constraint)
5. Writes timestamped JSON/TXT output files and uploads them as artifacts

### Workflow Triggers

- **Scheduled** — every 6 hours (`0 */6 * * *`)
- **Manual** — Actions tab → Crypto Sentiment Monitor → Run workflow

## Current Data Source

`fetch_crypto_news()` currently uses **hardcoded sample articles** for demonstration. Because URLs are unique, only the first run inserts data — subsequent runs are no-ops.

To get real accumulating data, replace the method body in `src/main.py` with a live source:

```python
# NewsAPI
resp = requests.get("https://newsapi.org/v2/everything", params={
    "q": "cryptocurrency", "apiKey": os.environ["NEWS_API_KEY"]
})

# CoinDesk RSS (no key required)
import feedparser
feed = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/")

# Reddit (no key required)
resp = requests.get("https://www.reddit.com/r/CryptoCurrency/new.json",
    headers={"User-Agent": "crypto-sentiment-monitor"})
```

## Database

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER / SERIAL | Auto-increment primary key |
| `title` | TEXT | Article headline |
| `content` | TEXT | Full article body |
| `url` | TEXT UNIQUE | Deduplication key |
| `published_date` | TIMESTAMP | Article publish time |
| `source` | TEXT | Publisher name |
| `sentiment_score` | REAL | TextBlob polarity (-1 to +1) |
| `crypto_mentioned` | TEXT | JSON array e.g. `["bitcoin","ethereum"]` |
| `created_at` | TIMESTAMP | Insert time |

**SQLite** is used by default (local file `src/crypto_sentiment.db`).  
**Vercel Postgres** is used automatically when the `POSTGRES_URL` repository secret is set.

## Output Files

Each run writes to `src/` (git-ignored) and uploads as `crypto-sentiment-results.zip`:

**`sentiment_summary_YYYYMMDD_HHMMSS.json`**
```json
{
  "timestamp": "20260529_140000",
  "summary": {
    "bitcoin": {
      "avg_sentiment": 0.25,
      "article_count": 15,
      "positive_count": 10,
      "negative_count": 3,
      "neutral_count": 2,
      "max_sentiment": 0.87,
      "min_sentiment": -0.12
    }
  },
  "total_cryptos": 3
}
```

**`articles_YYYYMMDD_HHMMSS.json`**
```json
{
  "articles": [
    {
      "title": "Bitcoin Reaches New High",
      "source": "CryptoNews",
      "sentiment_score": 0.8,
      "crypto_mentioned": ["bitcoin"],
      "published_date": "2026-05-29 14:00:00"
    }
  ],
  "total_articles": 15
}
```

**`sentiment_report_YYYYMMDD_HHMMSS.txt`** — human-readable summary  
**`crypto_sentiment.log`** — full execution log

## Project Structure

```
crypto-sentiment-monitor/
├── .github/workflows/
│   └── crypto-monitor.yml      # GitHub Actions workflow (checkout@v6, setup-python@v6, upload-artifact@v7)
├── src/
│   ├── main.py                 # NewsMonitor — fetches articles, scores sentiment, detects cryptos
│   ├── monitor_once.py         # GitHubActionsMonitor — single-run entry point, saves JSON/TXT output
│   ├── database.py             # DatabaseManager — SQLite / Vercel Postgres with automatic fallback
│   └── __init__.py
├── requirements.txt            # requests, textblob, psycopg2-binary
└── README.md
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/crypto-sentiment-monitor.git
cd crypto-sentiment-monitor
```

### 2. Enable GitHub Actions
Go to your repository → **Actions** tab → enable workflows if prompted.

### 3. Run your first analysis
Actions → **Crypto Sentiment Monitor** → **Run workflow**

### 4. Download results
Actions → latest run → scroll to **Artifacts** → download `crypto-sentiment-results.zip`

### Optional: Vercel Postgres
Add your `POSTGRES_URL` connection string as a repository secret (Settings → Secrets → Actions). The app detects it automatically and switches from SQLite to Postgres.

## Local Development

```bash
pip install -r requirements.txt
cd src && python monitor_once.py
```

Requires Python 3.9+. Uses SQLite locally (no secrets needed).

## Customization

**Add a cryptocurrency** — edit `crypto_keywords` in `src/main.py`:
```python
self.crypto_keywords = [
    'bitcoin', 'btc', ...,
    'yourtoken', 'tkr'   # add ticker + full name
]
```

**Change run frequency** — edit the cron in `.github/workflows/crypto-monitor.yml`:
```yaml
- cron: '0 */3 * * *'   # every 3 hours
```

## Troubleshooting

**Workflow not running** — check that GitHub Actions are enabled under Settings → Actions → General.

**No new data after first run** — expected with the sample data source. Wire up a real API in `fetch_crypto_news()` to get fresh articles each run.

**Artifacts missing** — artifacts expire after 30 days. Run the workflow again to generate new ones.
