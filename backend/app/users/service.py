"""ユーザの処理本体（ユーザ名での検索）。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User


def get_by_name(db: Session, name: str) -> User | None:
    """ユーザ名でユーザを取得する。

    Args:
        db: DB セッション。
        name: ユーザ名（完全一致）。

    Returns:
        見つかったユーザ。存在しなければ None。
    """
    return db.scalar(select(User).where(User.name == name))
