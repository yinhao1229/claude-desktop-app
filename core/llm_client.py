from __future__ import annotations

import time
from typing import Generator, Iterable, List, Optional

from .state import Message


class LLMClient:
    """Abstract client interface."""

    def send(
        self,
        messages: List[Message],
        system_prompt: str = "",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        api_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> str:
        raise NotImplementedError

    def stream(
        self,
        messages: List[Message],
        system_prompt: str = "",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        api_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> Iterable[str]:
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """Simple mock client that echoes the last user message."""

    def send(
        self,
        messages: List[Message],
        system_prompt: str = "",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        api_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> str:
        user_messages = [m for m in messages if m.role == "user"]
        if not user_messages:
            return "你好！我能为你做些什么？"
        prompt = user_messages[-1].content
        model_hint = f"（模型：{model or 'mock'}）" if model else ""
        return f"回声：{prompt} {model_hint}".strip()

    def stream(
        self,
        messages: List[Message],
        system_prompt: str = "",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        api_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> Generator[str, None, None]:
        response = self.send(messages, system_prompt, temperature, max_tokens, api_url, api_key, model)
        for chunk in response.split():
            yield chunk + " "
            time.sleep(0.1)
