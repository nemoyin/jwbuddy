import pytest
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app


@pytest.mark.asyncio
async def test_chat_no_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/chat", json={
            "session_id": "nonexistent",
            "message": "hello",
        })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/sessions", json={"title": "test"})
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["title"] == "test"


@pytest.mark.asyncio
async def test_list_sessions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
