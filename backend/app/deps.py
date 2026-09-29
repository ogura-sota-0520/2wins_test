"""エンドポイントの引数に自動で渡す DB セッションとログイン中ユーザの取得処理の定義。"""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.db import SessionLocal
from app.users.models import User

SESSION_COOKIE = "session_token"


def _get_db() -> Iterator[Session]:
    """リクエストごとに DB セッションを開き、終了時に閉じる。

    Yields:
        リクエスト中に使う DB セッション。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(_get_db)]


def _get_current_user(
    db: DbSession,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> User:
    """トークンから送信元のログイン中のユーザを取得する。

    Args:
        db: DB セッション。
        session_token: cookie に保存されたセッショントークン。

    Returns:
        ログイン中のユーザ。

    Raises:
        HTTPException: cookie がない、またはトークンが無効な場合（401）。
    """
    user = auth_service.get_user_by_token(db, session_token) if session_token else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "ログインしてください")
    return user


CurrentUser = Annotated[User, Depends(_get_current_user)]
