from __future__ import annotations
import json
from typing import AsyncIterator
from jwbuddy.llm.backends import LLMBackend
from jwbuddy.tools.registry import ToolRegistry
from jwbuddy.agent.memory import ConversationMemory
from jwbuddy.security.audit import audit_logger

SYSTEM_PROMPT = """你是 JWBuddy，纪检监察智能助手。
你可以使用工具来帮助用户查询和分析数据。
对于数据分析任务，先用工具查询数据，再分析结果。
如果结果需要可视化，请使用 chart 工具。
始终用中文回答，保持专业、客观。"""


class AgentRuntime:
    """ReAct Agent 运行时 — 思考-行动-观察循环"""

    def __init__(
        self,
        llm: LLMBackend,
        tools: ToolRegistry,
        system_prompt: str = SYSTEM_PROMPT,
    ):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = 10
        self._memories: dict[str, ConversationMemory] = {}

    async def run(
        self,
        message: str,
        session_id: str | None = None,
    ) -> AsyncIterator[dict]:
        """执行 Agent 循环，产出流式事件。
        事件类型: text, tool_call, tool_result, done, error
        """
        if session_id and session_id in self._memories:
            memory = self._memories[session_id]
        else:
            memory = ConversationMemory()
            memory.add_system(self.system_prompt)
            if session_id:
                self._memories[session_id] = memory
        memory.add_message("user", message)

        for iteration in range(self.max_iterations):
            # Step 1: LLM 思考
            yield {"type": "thinking", "content": ""}

            result = await self.llm.chat(
                messages=memory.get_messages(),
                tools=self.tools.openai_tools(),
            )

            content = result.content
            if not content.strip() and not result.tool_calls:
                yield {"type": "done", "content": "没有收到有效回复。"}
                return

            memory.add_message("assistant", content)

            # Check for native tool_calls first (OpenAI-compatible format)
            if result.tool_calls:
                for tc in result.tool_calls:
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        continue
                    tool_call = {"name": tc["function"]["name"], "args": args, "id": tc.get("id")}
                    yield {"type": "tool_call", "name": tool_call["name"], "args": tool_call["args"]}
                    audit_logger.log(
                        action=f"tool_call:{tool_call['name']}",
                        detail=f"args: {json.dumps(tool_call['args'], ensure_ascii=False)}",
                    )
                    tool_result = await self.tools.execute(tool_name=tool_call["name"], **tool_call["args"])

                    if tool_result.success:
                        result_text = json.dumps(tool_result.data, ensure_ascii=False, default=str)
                        yield {
                            "type": "tool_result",
                            "name": tool_call["name"],
                            "format": tool_result.format,
                            "data": tool_result.data,
                        }
                        memory.add_message("tool", result_text)
                    else:
                        yield {"type": "error", "content": tool_result.error}
                        memory.add_message("tool", f"Error: {tool_result.error}")
                # Continue the loop for next iteration
                continue

            # Try to parse tool call from response text
            tool_call = self._parse_tool_call(content)
            if not tool_call:
                # No tool call = final answer
                yield {"type": "text", "content": content}
                yield {"type": "done", "content": content}
                return

            # Step 2: Execute tool
            yield {"type": "tool_call", "name": tool_call["name"], "args": tool_call["args"]}
            audit_logger.log(
                action=f"tool_call:{tool_call['name']}",
                detail=f"args: {json.dumps(tool_call['args'], ensure_ascii=False)}",
            )
            tool_result = await self.tools.execute(tool_name=tool_call["name"], **tool_call["args"])

            if tool_result.success:
                result_text = json.dumps(tool_result.data, ensure_ascii=False, default=str)
                yield {
                    "type": "tool_result",
                    "name": tool_call["name"],
                    "format": tool_result.format,
                    "data": tool_result.data,
                }
                memory.add_message("tool", result_text)
            else:
                yield {"type": "error", "content": tool_result.error}
                memory.add_message("tool", f"Error: {tool_result.error}")

        yield {"type": "done", "content": "已达到最大迭代次数"}

    def _parse_tool_call(self, content: str) -> dict | None:
        """从 LLM 回复中解析工具调用"""
        # OpenAI function calling format
        import re
        match = re.search(r'{"name":\s*"([^"]+)"\s*,\s*"args":\s*({.*?})}', content, re.DOTALL)
        if match:
            name = match.group(1)
            args = json.loads(match.group(2))
            return {"name": name, "args": args}

        # Or just JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if "name" in data and "args" in data:
                    return data
            except json.JSONDecodeError:
                pass
        return None
