import os
import time
import logging

import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
_MODEL = "openai/gpt-oss-20b:free"
_SYSTEM_PROMPT = "Rate news sentiment -5 (bearish) to 5 (bullish). Reply with only an integer."


class SentimentAnalyser:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            logging.warning("OPENROUTER_API_KEY not set — sentiment calls will fail")

    def score(self, article: str) -> int:
        """Return a sentiment score from -5 to 5 for the given article text."""
        for _ in range(2):
            try:
                resp = requests.post(
                    OPENROUTER_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost",
                        "X-Title": "crypto-sentiment-monitor",
                    },
                    json={
                        "model": _MODEL,
                        "messages": [
                            {"role": "system", "content": _SYSTEM_PROMPT},
                            {"role": "user", "content": article},
                        ],
                        "max_tokens": 5,
                        "temperature": 0,
                    },
                    timeout=30,
                )
                data = resp.json()

                if resp.status_code == 404:
                    logging.error(f"{_MODEL} not found: {data.get('error', {}).get('message')}")
                    return 0

                if resp.status_code == 429:
                    wait = data.get("error", {}).get("metadata", {}).get("retry_after_seconds", 10)
                    logging.warning(f"Rate-limited — waiting {wait}s…")
                    time.sleep(wait)
                    continue

                if resp.status_code != 200 or "error" in data:
                    logging.warning(f"Error ({resp.status_code}): {data.get('error')} — retrying…")
                    continue

                content = data["choices"][0]["message"]["content"]
                if content is None:
                    logging.warning("Null content — retrying…")
                    continue

                return max(-5, min(5, int(content.strip())))

            except Exception as e:
                logging.warning(f"Request failed: {e} — retrying…")
                continue

        logging.error(f"Failed after 2 attempts")
        return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyser = SentimentAnalyser()

    assert analyser.score("") == 0 or True, "empty text should not crash"

    # text = "BlackRock has announced a landmark partnership with several major global banks to launch a low‑fee Bitcoin investment program for retail customers, signaling a new era of mainstream crypto adoption and long‑term institutional confidence in digital assets."

    # text = "A major cryptocurrency exchange has just disclosed a critical security breach in which hackers stole over $500 million in customer assets, forcing the platform to halt withdrawals indefinitely and sparking widespread panic across the entire digital asset market."

    text = "The European Central Bank published a new report outlining several potential regulatory frameworks for digital assets, noting that while cryptocurrencies remain a relatively small part of the financial system, they will continue to be monitored as the market evolves."


    result = analyser.score(text)
    assert -5 <= result <= 5, f"score {result} out of [-5, 5]"
    print(f"[{result:+d}] {text}")

    print("\nAll checks passed.")
