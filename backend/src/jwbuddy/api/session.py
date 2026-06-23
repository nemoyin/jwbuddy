from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["sessions"])

# In-memory session store (MVP; replace with Redis later)
_sessions: dict[str, dict] = {}


class SessionCreate(BaseModel):
    title: str = "新会话"


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int = 0


@router.post("")
async def create_session(data: SessionCreate):
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "id": session_id,
        "title": data.title,
        "created_at": datetime.now().isoformat(),
        "message_count": 0,
    }
    return SessionOut(**_sessions[session_id])


@router.get("")
async def list_sessions():
    return [SessionOut(**s) for s in _sessions.values()]
