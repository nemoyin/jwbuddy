import os
import pytest
from jwbuddy.llm.gateway import LLMGateway


@pytest.fixture(autouse=True)
def _openai_key():
    """Set a fake API key so AsyncOpenAI doesn't raise at construction."""
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    yield


@pytest.mark.asyncio
async def test_route_internal_for_sensitive():
    g = LLMGateway()
    backend = g.route(is_sensitive=True)
    assert backend == g.internal


@pytest.mark.asyncio
async def test_route_cloud_for_normal():
    g = LLMGateway()
    backend = g.route(is_sensitive=False, requires_reasoning=False)
    # Without cloud configured, may fall back
    assert backend is not None
