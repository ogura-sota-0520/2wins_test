"""メッセージの処理本体（送信・一覧取得）。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.messages.models import Message


def send_message(db: Session, room_id: int, sender_id: int, body: str) -> Message:
    """メッセージを保存する。

    Args:
        db: DB セッション。
        room_id: 送信先のルーム id。
        sender_id: 送信者のユーザ id。
        body: 本文。

    Returns:
        保存したメッセージ（id と送信日時を含む）。
    """
    # メッセージの保存
    message = Message(room_id=room_id, sender_id=sender_id, body=body)
    db.add(message)
    db.commit()
    # Message の created_at などは add 時に作成される → refresh でpython側に反映
    db.refresh(message)
    return message


def list_messages(
    db: Session,
    room_id: int,
    *,
    limit: int,
    before_id: int | None = None,
    after_id: int | None = None,
) -> tuple[list[Message], bool]:
    """ルームのメッセージをカーソル方式で取得する。

    - after_id 指定: after_id より新しいものを古い方から limit 件。
    - それ以外: before_id（未指定なら最新）より古いものを新しい方から limit 件。

    has_more を判定するため、内部では limit + 1 件取得する。

    Args:
        db: DB セッション。
        room_id: ルーム id。
        limit: 取得する最大件数。
        before_id: この id より古いメッセージを取得する。
        after_id: この id より新しいメッセージを取得する。

    Returns:
        id 昇順のメッセージと has_more の組。
        has_more は after_id 指定時はさらに新しいものが、それ以外はさらに古いものがあるかを表す。
        過去メッセージの読み込み停止 or 最新メッセージの読み込み継続 の判断に使用．
    """
    stmt = select(Message).where(Message.room_id == room_id)

    # 新着の取得（after_id より新しいものを古い順）
    if after_id is not None:
        stmt = stmt.where(Message.id > after_id).order_by(Message.id.asc())
        rows = list(db.scalars(stmt.limit(limit + 1)))
        return rows[:limit], len(rows) > limit

    # 最新または過去ログの取得（新しい順に取って昇順へ反転）
    if before_id is not None:
        stmt = stmt.where(Message.id < before_id)
    rows = list(db.scalars(stmt.order_by(Message.id.desc()).limit(limit + 1)))
    return list(reversed(rows[:limit])), len(rows) > limit
