"""ルーム API で受け取るリクエストと返すレスポンスの形式の定義。"""

from pydantic import BaseModel

from app.rooms.models import Room
from app.messages.models import Message
from app.messages.schemas import MessageOut
from app.users.schemas import UserName, UserOut


class RoomCreate(BaseModel):
    """ルーム作成のリクエストボディ。

    Attributes:
        partner_name: 相手のユーザ名。
    """

    partner_name: UserName


class RoomOut(BaseModel):
    """API で返すレスポンス形式のルーム情報。

    Attributes:
        id: ルーム id。
        members: 参加者（ユーザ id 昇順）。
        last_message: 最新メッセージ。まだなければ None。
    """

    id: int
    members: list[UserOut]
    last_message: MessageOut | None

    @classmethod
    def from_model(cls, room: Room, last_message: Message | None) -> "RoomOut":
        """ORM モデルからレスポンスを組み立てる。

        Args:
            room: ルームモデル。
            last_message: 最新メッセージ。まだなければ None。

        Returns:
            レスポンス用のルーム情報。
        """
        members = sorted(room.members, key=lambda m: m.user_id)
        return cls(
            id=room.id,
            members=[UserOut.model_validate(m.user) for m in members],
            last_message=MessageOut.model_validate(last_message) if last_message else None,
        )
