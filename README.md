# LLM Knowledge Extractor

Small FastAPI service that ingests unstructured text and uses OpenAI to produce:

- 1–2 sentence summary
- Extracted structured metadata (title, topics, sentiment, keywords, confidence)
- Persistence of all analyses in SQLite

## Features

- POST `/analyze` – analyze a single block of text
- GET `/search?topic=xyz` – search by topic or keyword substring
- GET `/health` – simple health check
- Edge cases handled: empty input (400), LLM failure (503 with clear message)
- Confidence score (naive heuristic)

## Quick Start

### 1. Environment

Install dependencies (Python 3.11+ recommended):

```bash
pip install -r requirements.txt
```


### 2. Set LLM Environment Variables

```bash
set OPENAI_API_KEY=your_key_here        
set OPENAI_MODEL=gpt-4o-mini            
set OPENAI_ENDPOINT=https://api.openai.com/v1   # optional custom base URL; if omitted default SDK endpoint is used

Only these three are recognized now. If `OPENAI_ENDPOINT` is provided it will be used as the `base_url`.
```

The service requires a valid key; if unavailable requests return 503.

### 3. Run

```bash
python main.py
```

Service default: http://127.0.0.1:8000

### 4. Example Requests

```bash
curl -X POST http://127.0.0.1:8000/analyze -H "Content-Type: application/json" \
	-d '{"text":"Product Launch Update\nWe had a great launch with excellent feedback from users and positive press coverage."}'

curl "http://127.0.0.1:8000/search?topic=launch"
```

### 5. Tests

```bash
pytest -q
```

## JSON Response Shape

```json
{
	"id": 1,
	"created_at": "2025-09-13T12:34:56.000Z",
	"original_text": "...",
	"summary": "1-2 sentence summary",
	"title": "Optional inferred title",
	"topics": ["topic1", "topic2", "topic3"],
	"sentiment": "positive|neutral|negative",
	"keywords": ["kw1", "kw2", "kw3"],
	"confidence": 0.73
}
```

## Design Choices (Why)

1. FastAPI + SQLite: extremely fast to scaffold, async-ready, and SQLite keeps deploy friction minimal.
2. Layered structure (`services`, `routes`, `models`, `schemas`) isolates concerns: API layer thin, logic testable.
3. Real OpenAI integration with deterministic system prompt; tests monkeypatch the call to avoid network.
4. Keyword extraction done locally via frequency + light noun-ish heuristic.
5. Confidence is intentionally simple: combines presence of fields plus brevity — easy to extend later.

## Trade-offs / Time Constraints

- No auth / rate limiting; would add if multi-user.
- Simple sentiment + topics heuristics; could replace with a model or classifier for accuracy.
- No pagination on search; acceptable for prototype scale.
- Minimal error taxonomy (400 for empty, 503 for LLM failure) to stay within time box.
- OpenAI call not fully streamed / no retries; could be enhanced with exponential backoff.
