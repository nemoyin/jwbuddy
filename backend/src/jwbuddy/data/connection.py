from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine


class DatabaseManager:
    """异步数据库连接管理器"""

    def __init__(self):
        self._engines: dict[str, AsyncEngine] = {}

    async def connect(self, name: str, url: str) -> bool:
        """注册并测试连接"""
        try:
            engine = create_async_engine(url, pool_size=5, max_overflow=10)
            async with engine.connect() as conn:
                await conn.execute(sa.text("SELECT 1"))
            self._engines[name] = engine
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {name}: {e}")

    def get_engine(self, name: str) -> AsyncEngine | None:
        return self._engines.get(name)

    async def execute(self, name: str, sql: str) -> list[dict]:
        """执行只读 SQL 查询"""
        engine = self._engines.get(name)
        if not engine:
            raise ValueError(f"Unknown datasource: {name}")
        async with engine.connect() as conn:
            result = await conn.execute(sa.text(sql))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns, row)) for row in rows]

    def list_connections(self) -> list[str]:
        return list(self._engines.keys())


db_manager = DatabaseManager()
