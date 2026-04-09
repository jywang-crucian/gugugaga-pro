from __future__ import annotations

import json
from pathlib import Path


CONFIG_PATH = Path("resources") / "config.json"


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_config(path: Path = CONFIG_PATH) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_config(config: dict, path: Path = CONFIG_PATH) -> None:
    _ensure_parent_dir(path)
    path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_saved_api_key(path: Path = CONFIG_PATH) -> str:
    value = load_config(path).get("DEEPSEEK_API_KEY", "")
    return value.strip() if isinstance(value, str) else ""


def set_saved_api_key(api_key: str, path: Path = CONFIG_PATH) -> None:
    config = load_config(path)
    config["DEEPSEEK_API_KEY"] = api_key.strip()
    save_config(config, path)
