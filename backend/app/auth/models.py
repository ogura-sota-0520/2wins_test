"""ログインセッション（トークンとユーザの対応）のテーブル定義。"""

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common import utcnow
from app.db import Base


class UserSession(Base):
    """ログインセッション。cookie のトークンとユーザを結び付ける。

    Attributes:
        token: cookie に保存するランダムなセッショントークン。
        user_id: セッションの持ち主のユーザ id。
        created_at: 作成日時（UTC）。
    """

    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
