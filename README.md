# Crypto Sentiment Monitor

An automated cryptocurrency news sentiment analysis application that monitors crypto news and analyzes market sentiment using natural language processing. Runs completely free on GitHub Actions with no server maintenance required.

## 🚀 Features

- 🔄 **Automated News Monitoring**: Analyzes cryptocurrency news articles for sentiment
- 📊 **Sentiment Analysis**: Uses TextBlob NLP to score sentiment from -1 (bearish) to +1 (bullish)
- 🪙 **Multi-Crypto Support**: Tracks Bitcoin, Ethereum, Dogecoin, and 8+ major cryptocurrencies
- 📈 **Trend Analysis**: Historical sentiment tracking and automated reporting
- 🤖 **GitHub Actions**: Automated runs every 6 hours - completely serverless
- 📁 **Downloadable Results**: JSON and text reports available as GitHub artifacts
- 🆓 **100% Free**: No API keys, servers, or paid services required

## 📊 Sentiment Scoring

- **🟢 Bullish** (>0.1): Positive market sentiment
- **🔴 Bearish** (<-0.1): Negative market sentiment  
- **🟡 Neutral** (-0.1 to 0.1): Mixed or neutral sentiment

## 🪙 Supported Cryptocurrencies

- Bitcoin (BTC)
- Ethereum (ETH) 
- Dogecoin (DOGE)
- Cardano (ADA)
- Solana (SOL)
- Polkadot (DOT)
- Chainlink (LINK)
- Litecoin (LTC)
- Polygon (MATIC)
- Avalanche (AVAX)
- Uniswap (UNI)

## 🤖 How It Works

### Automated GitHub Actions Workflow

The application runs automatically every 6 hours:

1. **Data Collection**: Fetches and analyzes cryptocurrency news articles
2. **Sentiment Analysis**: Processes each article to determine sentiment score
3. **Crypto Detection**: Identifies which cryptocurrencies are mentioned
4. **Report Generation**: Creates comprehensive sentiment summaries
5. **Artifact Upload**: Saves results as downloadable files

### Workflow Triggers
- ⏰ **Scheduled**: Every 6 hours automatically
- 🔄 **Manual**: Click "Run workflow" in GitHub Actions
- 📝 **Push**: Triggers on commits to main branch

## 📥 Getting Results

### Where to Find Your Reports

1. **Go to**: Your Repository → **Actions** tab
2. **Click**: Latest "Crypto Sentiment Monitor" workflow run  
3. **Scroll down**: To "Artifacts" section
4. **Download**: `crypto-sentiment-results.zip`

### What You Get

**📁 crypto-sentiment-results.zip contains:**

1. **`sentiment_summary_YYYYMMDD_HHMMSS.json`**
   ```json
   {
     "timestamp": "20250817_143000",
     "summary": {
       "bitcoin": {
         "avg_sentiment": 0.25,
         "article_count": 15,
         "positive_count": 10,
         "negative_count": 3,
         "neutral_count": 2
       }
     },
     "total_cryptos": 5
   }
   ```

2. **`articles_YYYYMMDD_HHMMSS.json`**
   ```json
   {
     "articles": [
       {
         "title": "Bitcoin Reaches New High",
         "sentiment_score": 0.8,
         "crypto_mentioned": ["bitcoin"],
         "source": "CryptoNews"
       }
     ]
   }
   ```

3. **`sentiment_report_YYYYMMDD_HHMMSS.txt`**
   ```
   🟢 BITCOIN: Bullish (0.250)
      📊 Articles: 15 | ✅ Positive: 10 | ❌ Negative: 3
   
   🔴 ETHEREUM: Bearish (-0.120)  
      📊 Articles: 12 | ✅ Positive: 4 | ❌ Negative: 8
   ```

4. **`crypto_sentiment.log`** - Detailed execution logs

### Live Results in GitHub Actions

You can also see real-time results in the workflow logs:

```
🎯 CRYPTO SENTIMENT SUMMARY
============================================================
🟢 BITCOIN: Bullish (0.250)
   📊 Articles: 15 | ✅ Positive: 10 | ❌ Negative: 3
🔴 ETHEREUM: Bearish (-0.120)
   📊 Articles: 12 | ✅ Positive: 4 | ❌ Negative: 8
🟡 DOGECOIN: Neutral (0.050)
   📊 Articles: 8 | ✅ Positive: 3 | ❌ Negative: 2
============================================================
```

## 🛠️ Setup Instructions

### 1. Fork or Clone This Repository
```bash
git clone https://github.com/YOUR_USERNAME/crypto-sentiment-monitor.git
cd crypto-sentiment-monitor
```

### 2. Enable GitHub Actions
- Go to your repository → **Actions** tab
- Click **"I understand my workflows, go ahead and enable them"**

### 3. Run Your First Analysis
- Click **Actions** → **Crypto Sentiment Monitor**
- Click **"Run workflow"** → **"Run workflow"**
- Wait 2-3 minutes for completion
- Download results from Artifacts section

### 4. Automatic Runs
The workflow will now run automatically every 6 hours!

## 🏗️ Project Structure

```
crypto-sentiment-monitor/
├── .github/workflows/
│   └── crypto-monitor.yml     # GitHub Actions workflow
├── src/
│   ├── __init__.py           # Package initializer
│   ├── main.py               # Core NewsMonitor class
│   ├── monitor_once.py       # Single-run script for GitHub Actions
│   └── database.py           # SQLite database management
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔧 Local Development (Optional)

### Prerequisites
- Python 3.9+
- pip

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run single analysis
cd src
python monitor_once.py
```

## 📊 Use Cases

- **💼 Investment Research**: Track sentiment trends before making crypto investments
- **📈 Market Analysis**: Identify bearish/bullish sentiment shifts
- **🔍 News Monitoring**: Stay updated on crypto market sentiment without manual tracking
- **📊 Data Analysis**: Export JSON data for further analysis in Excel/Python
- **🤖 Automation**: Set-and-forget sentiment monitoring

## 🆓 Why This Solution?

- **Zero Cost**: Runs entirely on GitHub's free tier
- **No Maintenance**: No servers to maintain or update
- **No API Keys**: No external services or rate limits
- **Reliable**: GitHub's infrastructure ensures consistent execution
- **Transparent**: All code is open source and auditable
- **Scalable**: Easy to add more cryptocurrencies or news sources

## 🔄 Customization

### Add More Cryptocurrencies
Edit `src/main.py` and add to the `crypto_keywords` list:
```python
self.crypto_keywords = [
    'bitcoin', 'btc', 'ethereum', 'eth',
    'your-new-crypto', 'ticker'  # Add here
]
```

### Change Run Frequency
Edit `.github/workflows/crypto-monitor.yml`:
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours instead of 6
```

### Add Real News Sources
Replace the sample articles in `fetch_crypto_news()` with real API calls to:
- NewsAPI
- CoinDesk RSS
- CoinTelegraph RSS
- Reddit API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test locally: `python src/monitor_once.py`
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Workflow Not Running?
- Check if GitHub Actions are enabled in your repository settings
- Verify the workflow file is in `.github/workflows/` directory

### No Artifacts Available?
- Make sure the workflow completed successfully (green checkmark)
- Artifacts are only kept for 30 days by default

### Want More Frequent Updates?
- Edit the cron schedule in the workflow file
- Remember: more frequent runs = more GitHub Actions minutes used

---

**📊 Start monitoring crypto sentiment automatically - no servers, no costs, just insights!**