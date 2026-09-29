"""アプリ本体の作成と起動時のテーブル作成、各 API ルータの登録。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

# テーブル定義を Base.metadata に登録するための全モデル読み込み
from app.auth import models as _auth_models  # noqa: F401
from app.auth.router import router as auth_router
from app.db import Base, engine
from app.messages import models as _messages_models  # noqa: F401
from app.messages.router import router as messages_router
from app.rooms import models as _rooms_models  # noqa: F401
from app.rooms.router import router as rooms_router
from app.users import models as _users_models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """起動時に未作成のテーブルを作成する。
    
    アプリ起動時に一度だけ呼ばれる。

    Yields:
        アプリケーションの稼働期間。
    """
    # テーブル作成
    Base.metadata.create_all(engine)
    yield


# アプリ本体とルータの登録
app = FastAPI(title="Simple Chat API", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(messages_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """死活監視用のエンドポイント。

    Returns:
        {"status": "ok"}。
    """
    return {"status": "ok"}
