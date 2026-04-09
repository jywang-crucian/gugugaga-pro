from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


HISTORY_PATH = Path("resources") / "chat_history.json"


def now_stamp() -> tuple[str, str]:
    dt = datetime.now()
    return dt.strftime("%H:%M:%S"), dt.isoformat()


def add_message(role: str, content: str) -> dict:
    ts, full_ts = now_stamp()
    return {
        "role": role,
        "content": content,
        "timestamp": ts,
        "full_time": full_ts,
    }


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_history(path: Path = HISTORY_PATH) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        # If file is corrupted, return empty conversation to keep app usable.
        return []
    return data if isinstance(data, list) else []


def save_history(messages: list[dict], path: Path = HISTORY_PATH) -> None:
    ensure_parent_dir(path)
    path.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
