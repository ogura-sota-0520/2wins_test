"""ルームの処理本体（1対1のルームの作成・取得、一覧取得、最新メッセージ取得）。"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.messages.models import Message
from app.rooms.models import Room, RoomMember
from app.users import service as users_service
from app.users.models import User


class PartnerNotFoundError(Exception):
    """相手のユーザが存在しない。"""


class SelfRoomError(Exception):
    """自分自身とのルームを作成しようとした。"""


class RoomNotFoundError(Exception):
    """ルームが存在しない、または参加していない。"""




def get_or_create_direct(db: Session, user: User, partner_name: str) -> tuple[Room, bool]:
    """相手との1対1のルームを取得し、なければ作成する。

    Args:
        db: DB セッション。
        user: ログイン中のユーザ。
        partner_name: 相手のユーザ名。

    Returns:
        ルームと、新規作成したかどうか。

    Raises:
        PartnerNotFoundError: 相手のユーザが存在しない場合。
        SelfRoomError: 相手が自分自身の場合。
    """
    # 相手の確認
    partner = users_service.get_by_name(db, partner_name)
    if partner is None:
        raise PartnerNotFoundError
    if partner.id == user.id:
        raise SelfRoomError

    # 既存のルームの検索
    low_id, high_id = sorted((user.id, partner.id))
    existing_room = _get_direct(db, low_id, high_id)
    if existing_room is not None:
        return existing_room, False

    # ルームと参加者の作成
    room = Room(
        direct_user_low_id=low_id,
        direct_user_high_id=high_id,
        members=[RoomMember(user_id=user.id), RoomMember(user_id=partner.id)],
    )
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        # 相手がほぼ同時に作成した場合の UNIQUE 制約違反、相手側のルームを返却
        db.rollback()
        existing_room = _get_direct(db, low_id, high_id)
        if existing_room is None:
            raise
        return existing_room, False
    return room, True


def get_for_member(db: Session, user: User, room_id: int) -> Room:
    """ユーザが参加しているルームを取得する。

    Args:
        db: DB セッション。
        user: ログイン中のユーザ。
        room_id: ルーム id。

    Returns:
        ルーム。

    Raises:
        RoomNotFoundError: ルームが存在しない、またはユーザが参加していない場合。
    """
    room = db.scalar(
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(Room.id == room_id, RoomMember.user_id == user.id)
    )
    if room is None:
        raise RoomNotFoundError
    return room


def list_for_user(db: Session, user: User) -> list[tuple[Room, Message | None]]:
    """ユーザが参加しているルームを最新メッセージ順に一覧する。

    メッセージのないルームは、メッセージのあるルームの後ろにルーム id 降順で並ぶ。

    Args:
        db: DB セッション。
        user: ログイン中のユーザ。

    Returns:
        ルームと、その最新メッセージ（なければ None）の組のリスト。
    """
    # 参加中のルームと最新メッセージの結合、最新メッセージ順の並べ替え
    stmt = (
        select(Room, Message)
        .join(RoomMember, RoomMember.room_id == Room.id)
        # last_message_id == NULLのルームも取得するため外部結合
        .outerjoin(Message, Message.id == Room.last_message_id)
        .where(RoomMember.user_id == user.id)
        .order_by(Room.last_message_id.desc().nulls_last(), Room.id.desc())
    )
    return [(room, message) for room, message in db.execute(stmt).all()]


def get_last_message(db: Session, room: Room) -> Message | None:
    """ルームの最新メッセージを取得する。

    Args:
        db: DB セッション。
        room: ルーム。

    Returns:
        最新メッセージ。まだなければ None。
    """
    if room.last_message_id is None:
        return None
    return db.get(Message, room.last_message_id)


def _get_direct(db: Session, low_id: int, high_id: int) -> Room | None:
    """2人のユーザ id から1対1のルームを取得する。

    Args:
        db: DB セッション。
        low_id: 小さい方のユーザ id。
        high_id: 大きい方のユーザ id。

    Returns:
        見つかったルーム。存在しなければ None。
    """
    return db.scalar(
        select(Room).where(Room.direct_user_low_id == low_id, Room.direct_user_high_id == high_id)
    )
