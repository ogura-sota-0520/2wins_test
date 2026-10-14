"""ルームとルーム参加者のテーブル定義。"""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common import utcnow
from app.db import Base
from app.users.models import User


class Room(Base):
    """ルーム（メッセージをやりとりする場）。

    Attributes:
        id: ルーム id。
        direct_user_low_id: 1対1のルームの参加者のうち小さい方のユーザ id。グループなら NULL。
        direct_user_high_id: 1対1のルームの参加者のうち大きい方のユーザ id。グループなら NULL。
        created_at: 作成日時（UTC）。
        members: ルームの参加者。
    """

    __tablename__ = "rooms"
    __table_args__ = (
        # 同じ2人の1対1のルームの重複防止（NULL を含む行は対象外のため、グループは制約を受けない）
        UniqueConstraint("direct_user_low_id", "direct_user_high_id"),
        # (1,2) と (2,1) を別物として登録させないための大小関係の強制
        CheckConstraint("direct_user_low_id < direct_user_high_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    direct_user_low_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    direct_user_high_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    # 1対多なので毎回DBにアクセスしないように lazy="selectin" でまとめて取得
    members: Mapped[list["RoomMember"]] = relationship(
        back_populates="room", lazy="selectin", cascade="all, delete-orphan"
    )


class RoomMember(Base):
    """ルームとユーザの参加関係。

    Attributes:
        room_id: ルーム id。
        user_id: 参加ユーザ id。
        room: 参加先のルーム。
        user: 参加ユーザ。
    """

    __tablename__ = "room_members"

    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)

    # Room.members で取得されるので lazy="joined" で毎回DBにアクセスしないようにする
    room: Mapped[Room] = relationship(back_populates="members")
    # 1対1なので毎回DBにアクセスしないように先に取得
    user: Mapped[User] = relationship(lazy="joined")
