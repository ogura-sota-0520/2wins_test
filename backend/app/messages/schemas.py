"""メッセージ API で受け取るリクエストと返すレスポンスの形式の定義。"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.common import UTCDateTime
from app.config import params

# 本文の入力制約（前後の空白を除いて 1〜body_max_length 文字）
_MessageBody = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=params.message.body_max_length),
]


class MessageCreate(BaseModel):
    """メッセージ送信のリクエストボディ。

    Attributes:
        body: 本文。
    """

    body: _MessageBody


class MessageOut(BaseModel):
    """API で返すメッセージ。

    Attributes:
        id: メッセージ id。
        room_id: 所属するルーム id。
        sender_id: 送信者のユーザ id。
        body: 本文。
        created_at: 送信日時（ミリ秒精度・末尾 Z の ISO 8601）。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    sender_id: int
    body: str
    created_at: UTCDateTime


class MessagePage(BaseModel):
    """メッセージ一覧の1ページ分。

    Attributes:
        messages: id 昇順のメッセージ。
        has_more: 取得範囲の先にまだメッセージがあるか。
    """

    messages: list[MessageOut]
    has_more: bool
