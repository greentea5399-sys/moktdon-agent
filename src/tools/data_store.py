"""Helpers to read and write data/*.json files. Copied from the café agent (Task 2)."""
import json

from src import config


def load(name: str) -> dict:
    """Read data/<name>.json and return it as a dict."""
    with open(config.DATA_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


def save(name: str, data: dict) -> None:
    """Write a dict to data/<name>.json."""
    with open(config.DATA_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
