"""メッセージ API（一覧・送信）のエンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.rooms import service as rooms_service
from app.config import params
from app.deps import CurrentUser, DbSession
from app.messages import service
from app.messages.schemas import MessageCreate, MessageOut, MessagePage
from app.users.models import User

router = APIRouter(prefix="/api/rooms/{room_id}/messages", tags=["messages"])


def _ensure_member(db: Session, user: User, room_id: int) -> None:
    """ユーザがルームの参加者であることを確認する。

    Args:
        db: DB セッション。
        user: ログイン中のユーザ。
        room_id: ルーム id。

    Raises:
        HTTPException: ルームが存在しない、または参加していない場合（404）。
    """
    try:
        rooms_service.get_for_member(db, user, room_id)
    except rooms_service.RoomNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ルームが見つかりません")


@router.get("")
def list_messages(
    room_id: int,
    db: DbSession,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=params.message.page_size_max)] = params.message.page_size,
    before_id: int | None = None,
    after_id: int | None = None,
) -> MessagePage:
    """ルームのメッセージを1ページ分返す。

    Args:
        room_id: ルーム id。
        db: DB セッション。
        user: ログイン中のユーザ。
        limit: 取得する最大件数（1〜page_size_max、既定は page_size）。
        before_id: この id より古いメッセージを取得する（過去ログ）。
        after_id: この id より新しいメッセージを取得する（新着）。

    Returns:
        id 昇順のメッセージと has_more。

    Raises:
        HTTPException: before_id と after_id を同時に指定した場合（422）、
            ルームに参加していない場合（404）。
    """
    # パラメータと参加者の検証
    if before_id is not None and after_id is not None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "before_id と after_id は同時に指定できません"
        )
    _ensure_member(db, user, room_id)
    # メッセージの取得
    messages, has_more = service.list_messages(
        db, room_id, limit=limit, before_id=before_id, after_id=after_id
    )
    return MessagePage(
        messages=[MessageOut.model_validate(m) for m in messages], has_more=has_more
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def send_message(
    room_id: int, body: MessageCreate, db: DbSession, user: CurrentUser
) -> MessageOut:
    """ルームにメッセージを送信する。

    Args:
        room_id: 送信先のルーム id。
        body: 本文。
        db: DB セッション。
        user: ログイン中のユーザ。

    Returns:
        保存したメッセージ。

    Raises:
        HTTPException: ルームに参加していない場合（404）。
    """
    _ensure_member(db, user, room_id)
    message = service.send_message(db, room_id, user.id, body.body)
    return MessageOut.model_validate(message)
