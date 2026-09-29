"""認証 API（登録・ログイン・ログアウト・ログイン中ユーザ取得）のエンドポイント定義。"""

from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.auth import service
from app.auth.schemas import Credentials
from app.deps import SESSION_COOKIE, CurrentUser, DbSession
from app.users.schemas import UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    """レスポンスにセッション cookie を設定する。

    Max-Age を付けないため、ブラウザを閉じると消えるセッション cookie になる。

    Args:
        response: cookie を設定するレスポンス。
        token: セッショントークン。
    """
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", path="/")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: Credentials, response: Response, db: DbSession) -> UserOut:
    """ユーザを登録してログインする。

    Args:
        body: 登録するユーザ名。
        response: セッション cookie を設定するレスポンス。
        db: DB セッション。

    Returns:
        作成したユーザ。

    Raises:
        HTTPException: ユーザ名が既に使われている場合（409）。
    """
    try:
        # 登録処理
        user, token = service.register(db, body.name)
    except service.UserAlreadyExistsError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "そのユーザ名は既に使われています。別の名前にしてください"
        )
    # cookie 設定
    _set_session_cookie(response, token)
    return UserOut.model_validate(user)


@router.post("/login")
def login(body: Credentials, response: Response, db: DbSession) -> UserOut:
    """既存ユーザとしてログインする。

    Args:
        body: ログインするユーザ名。
        response: セッション cookie を設定するレスポンス。
        db: DB セッション。

    Returns:
        ログインしたユーザ。

    Raises:
        HTTPException: ユーザが登録されていない場合（401）。
    """
    try:
        # ログイン処理
        user, token = service.login(db, body.name)
    except service.UserNotFoundError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "ユーザが登録されていません")
    # cookie 設定
    _set_session_cookie(response, token)
    return UserOut.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    db: DbSession,
    _user: CurrentUser,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> None:
    """サーバ側のセッションと cookie を削除してログアウトする。

    Args:
        response: cookie を削除するレスポンス。
        db: DB セッション。
        _user: ログイン中のユーザ（未ログインを 401 で弾くためだけに使用）。
        session_token: 削除するセッショントークン。
    """
    # サーバ側セッションの削除（CurrentUser が未ログインを弾くため token は必ず存在）
    if session_token:
        service.logout(db, session_token)
    # cookie の削除
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax")


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    """ログイン中のユーザを返す。

    Args:
        user: ログイン中のユーザ。

    Returns:
        ログイン中のユーザ。
    """
    return UserOut.model_validate(user)
