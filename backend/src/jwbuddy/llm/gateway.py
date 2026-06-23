from __future__ import annotations
from typing import AsyncIterator
from jwbuddy.config import settings
from jwbuddy.llm.backends import LLMBackend, OpenAICompatibleBackend, LLMResult


class LLMGateway:
    """LLM 路由网关 — 根据上下文选择合适的后端"""

    def __init__(self):
        self._internal: OpenAICompatibleBackend | None = None
        self._cloud: OpenAICompatibleBackend | None = None

    @property
    def internal(self) -> OpenAICompatibleBackend:
        if self._internal is None:
            self._internal = OpenAICompatibleBackend(
                base_url=settings.llm_internal_base_url,
                api_key=settings.llm_internal_api_key,
                model=settings.llm_internal_model,
            )
        return self._internal

    @property
    def cloud(self) -> OpenAICompatibleBackend:
        if self._cloud is None:
            self._cloud = OpenAICompatibleBackend(
                base_url=settings.llm_cloud_base_url,
                api_key=settings.llm_cloud_api_key,
                model=settings.llm_cloud_model,
            )
        return self._cloud

    def route(self, is_sensitive: bool = False, requires_reasoning: bool = False) -> LLMBackend:
        """路由决策: 涉密→内网, 复杂推理→内网, 否则→可回退"""
        if is_sensitive or requires_reasoning:
            return self.internal
        if settings.llm_fallback_enabled:
            return self.cloud
        return self.internal

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        is_sensitive: bool = False,
        requires_reasoning: bool = False,
        stream: bool = False,
    ) -> LLMResult | AsyncIterator[str]:
        backend = self.route(is_sensitive, requires_reasoning)
        if stream:
            return backend.chat_stream(messages, tools)
        return await backend.chat(messages, tools, stream=False)


gateway = LLMGateway()
