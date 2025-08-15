# Crypto Sentiment Monitor

An automated cryptocurrency news sentiment analysis application that monitors crypto news from multiple sources and analyzes market sentiment using natural language processing.

## Features

- 🔄 **Automated News Monitoring**: Fetches crypto news from multiple RSS feeds
- 📊 **Sentiment Analysis**: Analyzes sentiment using TextBlob NLP
- 🪙 **Multi-Crypto Support**: Tracks Bitcoin, Ethereum, and 8+ major cryptocurrencies
- 📈 **Trend Analysis**: Historical sentiment tracking and reporting
- 🤖 **GitHub Actions**: Automated runs every 3 hours
- 🚀 **Railway Deployment**: Easy cloud deployment option

## Supported News Sources

- CoinDesk
- Cointelegraph
- CryptoNews
- Bitcoin Magazine
- Decrypt

## Supported Cryptocurrencies

- Bitcoin (BTC)
- Ethereum (ETH)
- Cardano (ADA)
- Solana (SOL)
- Binance Coin (BNB)
- Ripple (XRP)
- Dogecoin (DOGE)
- Polygon (MATIC)
- Avalanche (AVAX)
- Chainlink (LINK)

## GitHub Actions Workflow

The application runs automatically every 3 hours using GitHub Actions:

1. Fetches latest crypto news
2. Analyzes sentiment for each article
3. Identifies cryptocurrency mentions
4. Generates summary reports
5. Uploads results as artifacts

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/crypto-sentiment-monitor.git
cd crypto-sentiment-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run single monitoring cycle:
```bash
cd src
python monitor_once.py
```

### Project Structure

```
crypto-sentiment-monitor/
├── .github/workflows/          # GitHub Actions configuration
├── src/                        # Source code
│   ├── main.py                # Main application (for Railway)
│   ├── monitor_once.py        # Single run version (for GitHub Actions)
│   └── database.py            # Database management
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Deployment Options

### GitHub Actions (Current)
- Runs every 3 hours automatically
- Results available as downloadable artifacts
- Completely free

### Railway (Next Step)
- 24/7 continuous monitoring
- Persistent database
- Web dashboard
- 500 hours/month free

## Output Files

Each run generates:
- `sentiment_summary_TIMESTAMP.json`: Aggregated sentiment data
- `articles_TIMESTAMP.json`: Individual article data
- `sentiment_report_TIMESTAMP.txt`: Human-readable report

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details