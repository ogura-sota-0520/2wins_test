"""ユーザのテーブル定義。"""

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.common import utcnow
from app.config import params
from app.db import Base


class User(Base):
    """ユーザ。

    Attributes:
        id: ユーザ id。
        name: ユーザ名（一意、大文字小文字を区別）。
        created_at: 登録日時（UTC）。
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(params.user.name_max_length), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
