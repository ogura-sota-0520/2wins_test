"""複数モジュールで使う日時ユーティリティ（現在の UTC 時刻、UTC 形式での JSON 出力）。"""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import PlainSerializer


def utcnow() -> datetime:
    """現在時刻を UTC で返す。

    Returns:
        タイムゾーン付きの現在時刻。
    """
    return datetime.now(UTC)


def _to_utc_iso(value: datetime) -> str:
    """日時をミリ秒精度・末尾 Z の ISO 8601 文字列に変換する。

    Args:
        value: 変換する日時。タイムゾーンなしの場合は UTC とみなす。

    Returns:
        "2026-01-01T00:00:00.000Z" 形式の文字列。
    """
    # SQLite から読み戻した日時はタイムゾーン情報なしのため UTC 扱い
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


UTCDateTime = Annotated[datetime, PlainSerializer(_to_utc_iso, return_type=str)]
