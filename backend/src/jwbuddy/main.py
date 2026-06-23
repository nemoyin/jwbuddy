from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jwbuddy.config import settings
from jwbuddy.api import chat, session
from jwbuddy.api import admin
from jwbuddy.data.connection import db_manager


def init_tools():
    """Initialize and register all tools with the tool registry.

    Called once at startup before any requests are handled.
    """
    from jwbuddy.tools.sql_query import SQLQueryTool
    from jwbuddy.tools.chart import ChartTool
    from jwbuddy.tools.document import DocumentTool
    from jwbuddy.llm.gateway import gateway
    from jwbuddy.tools.registry import registry

    tool = SQLQueryTool(llm_gateway=gateway, datasource="default")
    registry.register(tool)

    chart_tool = ChartTool(llm_gateway=gateway)
    registry.register(chart_tool)

    document_tool = DocumentTool()
    registry.register(document_tool)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init connections and register tools
    init_tools()
    yield
    # Shutdown: close connections
    await db_manager.dispose_all()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost", "https://tauri.localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(session.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}
