"""Unit tests for GrokBotDemo bot logic."""

from unittest.mock import MagicMock, patch
from src.bot import chat, create_client


def _make_mock_client(reply_text: str) -> MagicMock:
    """Return a mock OpenAI client that returns reply_text from chat.completions."""
    client = MagicMock()
    choice = MagicMock()
    choice.message.content = reply_text
    client.chat.completions.create.return_value = MagicMock(choices=[choice])
    return client


def test_chat_appends_user_and_assistant_to_history():
    client = _make_mock_client("Hello, hackathon!")
    history: list[dict] = []
    reply = chat(client, history, "Hi GrokBot")
    assert reply == "Hello, hackathon!"
    assert history[0] == {"role": "user", "content": "Hi GrokBot"}
    assert history[1] == {"role": "assistant", "content": "Hello, hackathon!"}


def test_chat_accumulates_multi_turn_history():
    client = _make_mock_client("Turn 2 reply")
    history: list[dict] = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "First reply"},
    ]
    chat(client, history, "Second message")
    assert len(history) == 4


def test_create_client_returns_openai_instance():
    with patch("src.bot.GROK_API_KEY", "test-key"), \
         patch("src.bot.GROK_BASE_URL", "https://api.x.ai/v1"):
        from openai import OpenAI
        client = create_client()
        assert isinstance(client, OpenAI)
