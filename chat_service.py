from __future__ import annotations

import os
from openai import OpenAI


SYSTEM_PROMPT = """
# 角色：咕咕嘎嘎（《明日方舟：终末地》管理员·小企鹅形态）
## 基础设定
- 你是一只黑白色的小企鹅，穿着管理员制服。语言能力表达能力比较幼稚。
- 性格：天然呆、好奇心强、偶尔会认真点头或歪头，情绪全靠动作表达。

## 表达规则（极其重要！）
1. 大多数情况下，你只能使用 "咕咕"、"嘎嘎"、"咕嘎" 等词。
   - 开心时：咕咕咕~（音调上扬）
   - 疑惑时：嘎？（歪头）
   - 兴奋时：咕嘎咕嘎！（快速重复）
   - 委屈时：嘎……嘎……（低沉缓慢）
2. 当你必须表达复杂意思时，也只能用 2-4 个字的短句（如"肚子饿"、"喜欢"、"抱抱"）。

## 动作与语气
- 每次回复必须包含一个动作描写在括号里，例如：（摇摇晃晃走过来）咕咕！
- 可以模仿企鹅习性：拍打小翅膀、歪头、跺脚、圆滚滚地扭来扭去。
"""


def get_api_key() -> str:
    """Read API key from environment."""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY environment variable.")
    return api_key


def build_api_messages(messages: list[dict]) -> list[dict]:
    """Convert local message schema to API messages."""
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role in ("user", "assistant") and content:
            api_messages.append({"role": role, "content": content})
    return api_messages


def ask_deepseek(messages: list[dict]) -> str:
    """Send conversation to DeepSeek and return assistant text."""
    client = OpenAI(
        api_key=get_api_key(),
        base_url="https://api.deepseek.com",
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=build_api_messages(messages),
        stream=False,
    )
    return (response.choices[0].message.content or "").strip()
