from __future__ import annotations

import time
from typing import Generator, Iterable, List, Optional

import httpx

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

    def list_models(self, api_url: str, api_key: str) -> List[str]:
        """Return available models for a provider."""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """Simple mock client that reflects the last user message with Markdown hints."""

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
        model_hint = f"> 使用模型：**{model or 'mock'}**\n\n" if model else ""
        return f"{model_hint}{prompt}\n\n- 自动回复仅供演示\n- 支持 **Markdown** 与 ```代码块``` 展示"

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
        for char in response:
            yield char
            time.sleep(0.01)

    def list_models(self, api_url: str, api_key: str) -> List[str]:
        # Mock返回一组演示模型
        return ["mock", "mock-plus", "mock-code"]


class OpenAICompatibleClient(LLMClient):
    """简单的 OpenAI 兼容客户端，仅演示获取模型列表。"""

    def list_models(self, api_url: str, api_key: str) -> List[str]:
        headers = {"Authorization": f"Bearer {api_key}"}
        url = api_url.rstrip("/") + "/models"
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        models = []
        for item in data.get("data", []) or data.get("models", []):
            model_id = item.get("id") if isinstance(item, dict) else None
            if model_id:
                models.append(model_id)
        return models

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
        raise NotImplementedError("仅示例获取模型列表，发送功能请自行实现")

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
        raise NotImplementedError("仅示例获取模型列表，流式功能请自行实现")
