"""Configuration loader for GrokBotDemo."""

import os
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY: str = os.environ["GROK_API_KEY"]
GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-3")
GROK_BASE_URL: str = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
