import pytest
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult
from jwbuddy.tools.registry import registry


class HelloTool(BaseTool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="hello",
            description="Says hello",
            parameters={
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Name"}},
                "required": ["name"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        name = kwargs.get("name", "world")
        return ToolResult(data=f"Hello, {name}!")


@pytest.mark.asyncio
async def test_register_and_execute():
    tool = HelloTool()
    registry.register(tool)
    result = await registry.execute("hello", name="JWBuddy")
    assert result.success
    assert result.data == "Hello, JWBuddy!"
