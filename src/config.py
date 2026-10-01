"""Load project settings from the .env file (copied from the café agent, Task 1)."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.md"

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))


def require_api_key() -> str:
    """Return the API key, or stop with a clear message if it is missing."""
    if not API_KEY or API_KEY.startswith("your_"):
        raise RuntimeError("API_KEY is missing. Copy .env.example to .env and put your API key in it.")
    return API_KEY
