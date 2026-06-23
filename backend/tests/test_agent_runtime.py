import pytest
from jwbuddy.agent.runtime import AgentRuntime, SYSTEM_PROMPT
from jwbuddy.agent.memory import ConversationMemory


@pytest.mark.asyncio
async def test_memory_add_system():
    mem = ConversationMemory()
    mem.add_system("You are a test bot.")
    assert len(mem.messages) == 1
    assert mem.messages[0]["role"] == "system"


@pytest.mark.asyncio
async def test_memory_sliding_window():
    mem = ConversationMemory(max_messages=5)
    mem.add_system("System")
    for i in range(10):
        mem.add_message("user", f"msg{i}")
    assert len(mem.messages) <= 5
    assert mem.messages[-1]["content"] == "msg9"


@pytest.mark.asyncio
async def test_parse_tool_call_json():
    runtime = AgentRuntime.__new__(AgentRuntime)
    result = runtime._parse_tool_call('{"name": "sql_query", "args": {"sql": "SELECT 1"}}')
    assert result is not None
    assert result["name"] == "sql_query"


@pytest.mark.asyncio
async def test_parse_tool_call_code_block():
    runtime = AgentRuntime.__new__(AgentRuntime)
    result = runtime._parse_tool_call('```json\n{"name": "hello", "args": {"name": "test"}}\n```')
    assert result is not None
    assert result["name"] == "hello"
