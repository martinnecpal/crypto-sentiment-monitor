# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (requires Python 3.9+)
pip install -r requirements.txt

# First-time setup: download TextBlob's NLTK corpus
python -c "import textblob; textblob.download_corpora()"

# Run a single sentiment analysis (must run from src/)
cd src && python monitor_once.py
```

The GitHub Actions workflow (`.github/workflows/crypto-monitor.yml`) runs `python monitor_once.py` from the `src/` directory on a 6-hour schedule and on manual dispatch (`workflow_dispatch`). Results are uploaded as artifacts (`crypto-sentiment-results.zip`) retained for 30 days. Actions use `checkout@v6`, `setup-python@v6`, `upload-artifact@v7` (all Node.js 24 native).

## Architecture

**Entry point**: `src/monitor_once.py` — runs a single analysis cycle, writes timestamped JSON/TXT output files to `src/`, and prints a summary to stdout for GitHub Actions logs.

**Core class hierarchy**:
- `DatabaseManager` (`src/database.py`) — supports both SQLite (default) and Vercel Postgres. Selects backend based on the `POSTGRES_URL` environment variable. Articles are stored with `crypto_mentioned` as a JSON-encoded list. Key methods: `get_sentiment_summary(days=N)` aggregates sentiment stats per crypto; `get_todays_articles(limit=50)` fetches today's records using backend-appropriate SQL (`CURRENT_DATE` for Postgres, `DATE('now')` for SQLite). Always use these methods rather than calling `_connect()` directly.
- `NewsMonitor` (`src/main.py`) — fetches articles, runs TextBlob sentiment scoring (`polarity` on article content, range -1 to +1), detects which cryptos are mentioned via word-boundary regex, then stores results via `DatabaseManager`.
- `GitHubActionsMonitor` (`src/monitor_once.py`) — subclass of `NewsMonitor` that adds `save_results_to_json()` for artifact output.

**Sentiment thresholds**: `> 0.1` = Bullish, `< -0.1` = Bearish, otherwise Neutral.

**Current data source**: `fetch_crypto_news()` in `src/main.py` uses 3 hardcoded sample articles with fixed URLs. Because the `url` column is `UNIQUE`, only the first run inserts data — all subsequent runs are no-ops. To get real accumulating data, replace the method body with a live source (NewsAPI, CoinDesk RSS, Reddit). The crypto keyword list in `NewsMonitor.__init__` is the single place to add new coins; ticker aliases (e.g. `btc` → `bitcoin`) are normalized in `identify_cryptos()`.

**Database**: SQLite file `crypto_sentiment.db` by default (local, git-ignored). If `POSTGRES_URL` is set (e.g. via GitHub secret for Vercel Postgres), the app switches to Postgres automatically. Never add raw SQL directly to `monitor_once.py` — always add a method to `DatabaseManager` that handles both backends.

**SQL placeholder pattern**: `DatabaseManager` sets `self.ph = "%s"` for Postgres and `"?"` for SQLite. Any new queries added to the class must use `{self.ph}` (or the local `ph = self.ph` alias) rather than hardcoded placeholders.

**Alias normalization gap**: `identify_cryptos()` only maps three tickers to canonical names (`btc`→`bitcoin`, `eth`→`ethereum`, `doge`→`dogecoin`). All other tickers in `crypto_keywords` (e.g. `ada`, `sol`, `dot`) are stored as-is, so adding a new coin requires both a `crypto_keywords` entry and a normalization branch in `identify_cryptos()` if you want a canonical name.

**Aggregation is done in Python, not SQL**: `get_sentiment_summary()` fetches all matching rows and computes stats with `statistics.mean` etc. in memory. For large datasets this won't scale — move aggregation to SQL if row counts grow.

**Output files** (written to `src/` at runtime, git-ignored):
- `sentiment_summary_<ts>.json` — per-crypto aggregated stats
- `articles_<ts>.json` — individual article records
- `sentiment_report_<ts>.txt` — human-readable text report
- `crypto_sentiment.log` — execution log
- `crypto_sentiment.db` — SQLite database
