"""GrokBotDemo — a conversational bot powered by the xAI Grok API."""

from openai import OpenAI
from src.config import GROK_API_KEY, GROK_BASE_URL, GROK_MODEL

SYSTEM_PROMPT = (
    "You are GrokBot, a helpful AI assistant built for the Meetup Hackathon. "
    "Be concise, friendly, and accurate."
)


def create_client() -> OpenAI:
    """Create an OpenAI-compatible client pointed at the xAI Grok endpoint."""
    return OpenAI(api_key=GROK_API_KEY, base_url=GROK_BASE_URL)


def chat(client: OpenAI, history: list[dict], user_message: str) -> str:
    """Send a user message and return the assistant reply."""
    history.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model=GROK_MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
    )
    reply = response.choices[0].message.content or ""
    history.append({"role": "assistant", "content": reply})
    return reply


def main() -> None:
    """Run GrokBot as an interactive CLI."""
    client = create_client()
    history: list[dict] = []
    print("GrokBot is ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue
        reply = chat(client, history, user_input)
        print(f"GrokBot: {reply}\n")


if __name__ == "__main__":
    main()
