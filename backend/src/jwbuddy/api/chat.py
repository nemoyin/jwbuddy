from __future__ import annotations
import json
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from jwbuddy.agent.runtime import AgentRuntime
from jwbuddy.llm.gateway import gateway
from jwbuddy.tools.registry import registry

router = APIRouter(prefix="/chat", tags=["chat"])

# In-memory agents per session (MVP)
_agents: dict[str, AgentRuntime] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    sensitive: bool = False


def _get_or_create_agent(session_id: str) -> AgentRuntime:
    if session_id not in _agents:
        backend = gateway.route(is_sensitive=False)
        _agents[session_id] = AgentRuntime(llm=backend, tools=registry)
    return _agents[session_id]


@router.post("")
async def chat(req: ChatRequest):
    if req.session_id not in _agents:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = _agents[req.session_id]

    async def event_generator():
        async for event in agent.run(req.message, req.session_id):
            yield {"event": event["type"], "data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(event_generator())
