import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

_FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "openai/gpt-oss-20b:free",
]

class HeadlineDeduplicator:
    def __init__(self):
        self._seen: set[str] = set()
        self.api_key: str = os.environ.get("OPENROUTER_API_KEY", "")

    def extract_titles(self, articles: list[dict]) -> tuple[list[dict], int]:
        seen: set[str] = set()
        unique = []
        for article in articles:
            title = article.get("title", "").strip()
            if title and title not in seen:
                seen.add(title)
                unique.append(article)
        removed = len(articles) - len(unique)
        return unique, removed

    def reset(self):
        self._seen.clear()

    def _post_with_retry(self, payload: dict, rounds: int = 2) -> dict:
        """Cycle through free models, trying each once per round before retrying."""
        rate_limited: dict[str, float] = {}

        for _ in range(rounds):
            for model in _FREE_MODELS:
                payload["model"] = model
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost",
                        "X-Title": "crypto-sentiment-monitor",
                    },
                    json=payload,
                    timeout=60,
                )
                data = resp.json()

                if resp.status_code == 429:
                    wait = (
                        data.get("error", {})
                            .get("metadata", {})
                            .get("retry_after_seconds", 10)
                    )
                    print(f"{model} rate-limited (retry in {wait}s), trying next model…")
                    rate_limited[model] = wait
                    continue

                if resp.status_code != 200 or "error" in data:
                    print(f"{model} error ({resp.status_code}): {data.get('error')}")
                    continue

                return data

            # All models exhausted in this round — wait for the shortest backoff
            if rate_limited:
                wait = min(rate_limited.values())
                print(f"All models rate-limited, waiting {wait}s before retry…")
                time.sleep(wait)
                rate_limited.clear()

        raise RuntimeError("All free models failed or were rate-limited")

    def simplest_prompt_AI(self) -> str:
        payload = {
            "model": _FREE_MODELS[0],
            "messages": [
                {"role": "user", "content": "What is the best personal growth experience?"}
            ],
        }
        data = self._post_with_retry(payload)
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("No choices in OpenRouter response")
        return choices[0].get("message", {}).get("content", "")

    def dedupe_titles_with_AI(self, items: list[dict]) -> list[dict]:
        if not items:
            return []

        try:
            titles = [(item.get("title") or "").strip() for item in items]

            payload = {
                "model": _FREE_MODELS[0],
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a news deduplication assistant. "
                            "Return only valid JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": "Deduplicate these titles:\n\n"
                            + "\n".join(f"{i}: {t}" for i, t in enumerate(titles)),
                    },
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "dedupe_titles",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "keep_indices": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                }
                            },
                            "required": ["keep_indices"],
                            "additionalProperties": False,
                        },
                    },
                },
            }

            data = self._post_with_retry(payload)

            choices = data.get("choices")
            if not choices:
                raise RuntimeError(f"Missing choices in response: {data}")

            content = choices[0].get("message", {}).get("content")
            if not content:
                raise RuntimeError(f"Missing content in response: {data}")

            parsed = json.loads(content)
            keep_indices = sorted(set(parsed["keep_indices"]))
            return [items[i] for i in keep_indices if 0 <= i < len(items)]

        except Exception as e:
            print("AI dedupe failed, fallback to exact-title dedupe:", e)
            unique, _ = self.extract_titles(items)
            return unique
