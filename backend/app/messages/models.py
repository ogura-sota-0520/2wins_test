"""メッセージのテーブル定義。"""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common import utcnow
from app.db import Base


class Message(Base):
    """ルーム内のメッセージ。

    Attributes:
        id: メッセージ id。単調増加で、ページングのカーソルとして使う。
        room_id: 所属するルーム id。
        sender_id: 送信者のユーザ id。
        body: 本文。
        created_at: 送信日時（UTC）。
    """

    __tablename__ = "messages"
    __table_args__ = (
        # (room_id, id) の順に並べたインデックスを作成．before_id / after_id による範囲取得の高速化
        Index("ix_messages_room_id_id", "room_id", "id"),
        # 削除された id の再利用防止（カーソル用に単調増加を保証）．メッセージ削除機能のための拡張性担保
        {"sqlite_autoincrement": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
