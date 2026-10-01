# GrokBotDemo — Architecture

## Overview

GrokBotDemo is a lightweight Python CLI chatbot that proxies conversations to the xAI Grok model via its OpenAI-compatible REST API.

## Request Flow

```
User (CLI)
    │  user message
    ▼
bot.py::chat()
    │  POST /v1/chat/completions
    │  model: grok-4.3
    │  messages: [system, ...history, user]
    ▼
xAI Grok API (api.x.ai)
    │  assistant reply
    ▼
bot.py  →  prints reply  →  appends to history
```

## Modules

| Module | Responsibility |
|--------|---------------|
| `src/config.py` | Reads `GROK_API_KEY`, `GROK_MODEL`, `GROK_BASE_URL` from environment |
| `src/bot.py` | Creates the API client, manages conversation history, runs the CLI loop |
| `tests/test_bot.py` | Unit tests using mocked OpenAI client |

## Design Decisions

- Uses the `openai` SDK (not a custom HTTP client) because xAI's API is OpenAI-compatible — no extra dependency needed.
- Conversation history is an in-memory list; persistence can be added later.
- Config is read once at import time from environment variables (`.env` via `python-dotenv`).
