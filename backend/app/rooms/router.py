"""ルーム API（一覧・作成・取得）のエンドポイント定義。"""

from fastapi import APIRouter, HTTPException, Response, status

from app.rooms import service
from app.rooms.schemas import RoomCreate, RoomOut
from app.deps import CurrentUser, DbSession

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("")
def list_rooms(db: DbSession, user: CurrentUser) -> list[RoomOut]:
    """参加中のルームを最終更新日時（最新メッセージ、なければ作成日時）の新しい順に返す。

    Args:
        db: DB セッション。
        user: ログイン中のユーザ。

    Returns:
        ルームのリスト。
    """
    return [
        RoomOut.from_model(room, last_message)
        for room, last_message in service.list_for_user(db, user)
    ]


@router.post("", responses={201: {"description": "新規作成"}, 200: {"description": "既存のルーム"}})
def create_room(
    body: RoomCreate, response: Response, db: DbSession, user: CurrentUser
) -> RoomOut:
    """相手との1対1のルームを作成する。既にあればそれを返す。

    Args:
        body: 相手のユーザ名。
        response: ステータスコードを設定するレスポンス。
        db: DB セッション。
        user: ログイン中のユーザ。

    Returns:
        作成した、または既存のルーム。

    Raises:
        HTTPException: 相手が存在しない場合（404）、相手が自分自身の場合（400）。
    """
    # ルームの取得または作成
    try:
        room, is_new = service.get_or_create_direct(db, user, body.partner_name)
    except service.PartnerNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ユーザが見つかりません")
    except service.SelfRoomError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "自分自身とはルームを作成できません")
    # 新規なら 201、既存なら 200
    response.status_code = status.HTTP_201_CREATED if is_new else status.HTTP_200_OK
    return RoomOut.from_model(room, service.get_last_message(db, room))


@router.get("/{room_id}")
def get_room(room_id: int, db: DbSession, user: CurrentUser) -> RoomOut:
    """参加中のルームを1件返す。メッセージ一覧画面の相手名表示に使用．

    Args:
        room_id: ルーム id。
        db: DB セッション。
        user: ログイン中のユーザ。

    Returns:
        ルーム。

    Raises:
        HTTPException: ルームが存在しない、または参加していない場合（404）。
    """
    try:
        room = service.get_for_member(db, user, room_id)
    except service.RoomNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ルームが見つかりません")
    return RoomOut.from_model(room, service.get_last_message(db, room))
