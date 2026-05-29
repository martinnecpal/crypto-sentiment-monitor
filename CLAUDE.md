# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run a single sentiment analysis (must run from src/)
cd src && python monitor_once.py
```

The GitHub Actions workflow (`.github/workflows/crypto-monitor.yml`) runs `python monitor_once.py` from the `src/` directory on a 6-hour schedule and on pushes to main. Results are uploaded as artifacts (`crypto-sentiment-results.zip`) retained for 30 days.

## Architecture

**Entry point**: `src/monitor_once.py` — runs a single analysis cycle, writes timestamped JSON/TXT output files to `src/`, and prints a summary to stdout for GitHub Actions logs.

**Core class hierarchy**:
- `DatabaseManager` (`src/database.py`) — wraps a local SQLite file (`crypto_sentiment.db`). Articles are stored with `crypto_mentioned` as a JSON-encoded list. `get_sentiment_summary(days=N)` aggregates sentiment stats per crypto for the last N days.
- `NewsMonitor` (`src/main.py`) — fetches articles, runs TextBlob sentiment scoring (`polarity` on article content, range -1 to +1), detects which cryptos are mentioned via word-boundary regex, then stores results via `DatabaseManager`.
- `GitHubActionsMonitor` (`src/monitor_once.py`) — subclass of `NewsMonitor` that adds `save_results_to_json()` for artifact output.

**Sentiment thresholds**: `> 0.1` = Bullish, `< -0.1` = Bearish, otherwise Neutral.

**Current data source**: `fetch_crypto_news()` uses hardcoded sample articles. To connect real sources (NewsAPI, CoinDesk RSS, Reddit), replace that method's body. The crypto keyword list in `NewsMonitor.__init__` is the single place to add new coins; ticker aliases (e.g. `btc` → `bitcoin`) are normalized in `identify_cryptos()`.

**Output files** (written to `src/` at runtime, git-ignored):
- `sentiment_summary_<ts>.json` — per-crypto aggregated stats
- `articles_<ts>.json` — individual article records
- `sentiment_report_<ts>.txt` — human-readable text report
- `crypto_sentiment.log` — execution log
- `crypto_sentiment.db` — SQLite database
