"""認証の処理本体（ユーザ登録・ログイン・ログアウト・トークンからのユーザ取得）。"""

import secrets

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.models import UserSession
from app.users import service as users_service
from app.users.models import User


class UserAlreadyExistsError(Exception):
    """登録しようとしたユーザ名が既に使われている。"""


class UserNotFoundError(Exception):
    """ログインしようとしたユーザが存在しない。"""


def register(db: Session, name: str) -> tuple[User, str]:
    """ユーザを新規登録し、そのままログイン状態にする。

    Args:
        db: DB セッション。
        name: 登録するユーザ名。

    Returns:
        作成したユーザと、発行したセッショントークン。

    Raises:
        UserAlreadyExistsError: 同じユーザ名が既に存在する場合。
    """
    # ユーザ作成（UNIQUE 制約違反で重複名を検出）
    user = User(name=name)
    db.add(user)
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise UserAlreadyExistsError from e
    # セッション発行
    token = _create_session(db, user.id)
    db.commit()
    return user, token


def login(db: Session, name: str) -> tuple[User, str]:
    """既存ユーザとしてログインし、新しいセッションを発行する。

    Args:
        db: DB セッション。
        name: ログインするユーザ名。

    Returns:
        ログインしたユーザと、発行したセッショントークン。

    Raises:
        UserNotFoundError: ユーザが存在しない場合。
    """
    # ユーザの存在確認
    user = users_service.get_by_name(db, name)
    if user is None:
        raise UserNotFoundError
    # セッション発行
    token = _create_session(db, user.id)
    db.commit()
    return user, token


def logout(db: Session, token: str) -> None:
    """セッションを削除してログアウトする。

    Args:
        db: DB セッション。
        token: 削除するセッショントークン。
    """
    db.execute(delete(UserSession).where(UserSession.token == token))
    db.commit()


def get_user_by_token(db: Session, token: str) -> User | None:
    """セッショントークンからユーザを取得する。

    Args:
        db: DB セッション。
        token: セッショントークン。

    Returns:
        トークンに対応するユーザ。無効なトークンなら None。
    """
    return db.scalar(
        select(User)
        .join(UserSession, UserSession.user_id == User.id)
        .where(UserSession.token == token)
    )


def _create_session(db: Session, user_id: int) -> str:
    """セッションを作成する。

    Args:
        db: DB セッション。
        user_id: セッションを発行するユーザ id。

    Returns:
        発行したセッショントークン。
    """
    token = secrets.token_urlsafe(32)
    db.add(UserSession(token=token, user_id=user_id))
    return token
