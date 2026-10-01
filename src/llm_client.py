"""Thin wrapper around the OpenAI-compatible chat API (Groq or xAI). Copied from the café agent (Task 1)."""
from openai import OpenAI

from src import config

_client = None


def _get_client() -> OpenAI:
    """Create the client once, the first time it is needed."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=config.require_api_key(), base_url=config.BASE_URL)
    return _client


def chat(messages: list[dict], tools: list[dict] | None = None):
    """Send messages (and optional tool schemas) to the LLM and return the assistant message."""
    kwargs = {"model": config.MODEL, "messages": messages}
    if tools is not None:
        kwargs["tools"] = tools
    response = _get_client().chat.completions.create(**kwargs)
    return response.choices[0].message


if __name__ == "__main__":
    print(chat([{"role": "user", "content": "Hello"}]).content)
