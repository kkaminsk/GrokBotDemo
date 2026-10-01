# GrokBotDemo 🤖

> A conversational AI bot powered by [xAI Grok](https://x.ai), built for the **Meetup Hackathon**.

---

## What It Does

GrokBotDemo is an AI agent that connects to the Grok API to answer questions, assist with tasks, and demonstrate agentic coding capabilities — all from a simple Python interface.

The main feature in progress is a reply follow-up bot for X: it finds replies to your posts that deserve a response and emails you a digest with Grok-drafted suggested replies. See [spec.md](spec.md) for the full specification.

---

## Architecture

```
/
├── README.md         # You are here
├── AGENTS.md         # Persistent instructions for Grok Bot / AI agents
├── spec.md           # X reply follow-up bot specification
├── .gitignore        # Excludes secrets, build output, local state
├── .env.example      # Template for required environment variables
├── requirements.txt  # Python dependencies
├── src/
│   ├── bot.py        # Core bot logic & Grok API integration
│   └── config.py     # Configuration loading
├── tests/
│   └── test_bot.py   # Unit tests
└── docs/
    └── architecture.md
```

---

## Prerequisites

- Python 3.11+
- A [Grok API key](https://console.x.ai)

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/kkaminsk/GrokBotDemo.git
cd GrokBotDemo

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GROK_API_KEY
```

---

## Running the Bot

```bash
python -m src.bot
```

---

## Running Tests

```bash
pytest
```

---

## Linting

```bash
ruff check .
```

---

## Configuration

All configuration is done via environment variables. See `.env.example` for the full list. **Never commit your `.env` file.**

---

## Contributing

1. Create a feature branch.
2. Make small, focused changes.
3. Run lint + tests before committing.
4. Open a pull request.

---

## License

MIT
