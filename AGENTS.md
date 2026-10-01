# Repository Instructions for AI Agents (Grok Bot)

## Project

GrokBotDemo is a Python-based conversational AI bot that uses the xAI Grok API.
It was created for the Meetup Hackathon.

## Development Rules

- Do **not** commit secrets, API keys, or `.env` files.
- Do **not** modify production configuration directly.
- Run tests before committing changes: `pytest`
- Run the linter before committing: `ruff check .`
- Prefer small, focused changes — one concern per commit.
- Do **not** modify generated files or dependency lock files manually.
- All new features must have corresponding tests in `/tests`.

## Commands

Install dependencies:
```
pip install -r requirements.txt
```

Run the bot:
```
python src/bot.py
```

Lint:
```
ruff check .
```

Test:
```
pytest
```

## Architecture

| Path | Purpose |
|------|---------|
| `/src/bot.py` | Core bot logic and Grok API integration |
| `/src/config.py` | Configuration and environment variable loading |
| `/tests/` | Unit tests (pytest) |
| `/docs/` | Architecture and design documentation |

## Environment Variables

All secrets come from environment variables loaded via `.env` (never committed).
See `.env.example` for the full list of required variables.

## Key Dependency

- `openai` SDK (used to call the Grok API via xAI's OpenAI-compatible endpoint)
- `python-dotenv` for `.env` loading
- `pytest` + `ruff` for testing and linting
