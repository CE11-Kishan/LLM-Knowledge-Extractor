from __future__ import annotations
import os
from typing import List, Tuple
import json

try:
    from openai import OpenAI
    try:
        from openai import AzureOpenAI
    except Exception:
        AzureOpenAI = None  # type: ignore
except Exception as e:
    raise RuntimeError("openai package not installed") from e

_cached: dict | None = None

ALLOWED_SENTIMENTS = {"positive", "negative", "neutral"}

def get_client():
    """Return a cached OpenAI (or Azure OpenAI) client and model name.

    Environment variables:
      - OPENAI_API_KEY (required)
      - OPENAI_MODEL (required))
      - OPENAI_ENDPOINT (optional base URL or Azure resource endpoint)
      - AZURE_OPENAI_API_VERSION (if set with endpoint -> Azure client is used, model becomes deployment name)
    """
    global _cached

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")

    if not os.getenv("OPENAI_MODEL"):
        raise RuntimeError("OPENAI_MODEL not configured")

    model = os.getenv("OPENAI_MODEL")
    endpoint = os.getenv("OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    cache_key = (api_key, endpoint, api_version)
    if _cached and _cached.get("key") == cache_key:
        return _cached["client"], model

    try:
        # Azure mode
        if api_version and endpoint and AzureOpenAI is not None:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint.rstrip('/'),
            )
        else:
            # Standard OpenAI (optionally with custom base endpoint)
            if endpoint:
                client = OpenAI(api_key=api_key, base_url=endpoint.rstrip('/'))
            else:
                client = OpenAI(api_key=api_key)

        _cached = {"client": client, "key": cache_key}
        return client, model
    except Exception as e:
        raise RuntimeError("Failed to initialize LLM client") from e


def extract_text_insights(text: str) -> Tuple[str, List[str], str | None, str | None]:
    if not text.strip():
        raise RuntimeError("Empty text provided to LLM")
    client, model = get_client()

    system = (
        "You generate ONLY JSON with keys: summary, topics, title, sentiment.\n"
        "- summary: concise 1-2 sentence overview.\n"
        "- topics: array of EXACTLY 3 broad themes (single or two-word phrases).\n"
        "- title: short, relevant headline summarizing the main idea of the text short headline (null if no clear title).\n"
        "- sentiment: one of positive, negative, neutral.\n"
        "Respond ONLY with valid minified JSON: {\"summary\":...,\"topics\":[...],\"title\":...,\"sentiment\":...}"
    )

    prompt = text.strip()[:8000]
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = resp.choices[0].message.content
        data = json.loads(content)

        raw_summary = data.get("summary")
        raw_topics = data.get("topics")
        raw_title = data.get("title")
        raw_sentiment = data.get("sentiment")

        summary = str(raw_summary) if raw_summary is not None else ""

        topics: List[str] = []
        if isinstance(raw_topics, list):
            for t in raw_topics[:3]:  # keep at most 3
                topics.append(str(t)[:40])

        title: str | None
        if raw_title is None:
            title = None
        else:
            title = str(raw_title)[:120]

        sentiment_value: str | None = None
        if isinstance(raw_sentiment, str):
            sv = raw_sentiment.strip().lower()
            if sv in ALLOWED_SENTIMENTS:
                sentiment_value = sv

        return summary, topics, title, sentiment_value
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}") from e
