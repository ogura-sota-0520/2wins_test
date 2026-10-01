"""リポジトリ直下の config/params.json から読み込むアプリのパラメタ定義"""

from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, PositiveInt, model_validator
from pydantic.alias_generators import to_camel

# 共有パラメタファイルのパス
PARAMS_PATH = Path(__file__).resolve().parents[2] / "config" / "params.json"


class _Section(BaseModel):
    """各セクション共通の設定（camelCase キーの受け付け、未知キーの拒否、変更不可）"""

    model_config = ConfigDict(alias_generator=to_camel, extra="forbid", frozen=True)


class UserParams(_Section):
    """ユーザに関するパラメタ

    Attributes:
        name_max_length: ユーザ名の最大文字数
    """

    name_max_length: PositiveInt


class MessageParams(_Section):
    """メッセージに関するパラメタ

    Attributes:
        body_max_length: 本文の最大文字数
        page_size: 一覧取得の既定件数
        page_size_max: 一覧取得で指定できる最大件数
    """

    body_max_length: PositiveInt
    page_size: PositiveInt
    page_size_max: PositiveInt

    @model_validator(mode="after")
    def _check_page_size(self) -> Self:
        """既定件数が最大件数以下であることを検証する

        Returns:
            検証済みのインスタンス

        Raises:
            ValueError: page_size が page_size_max を超える場合
        """
        if self.page_size > self.page_size_max:
            raise ValueError("pageSize は pageSizeMax 以下にしてください")
        return self


class Params(BaseModel):
    """バックエンドで使うパラメタ全体

    Attributes:
        user: ユーザに関するパラメタ
        message: メッセージに関するパラメタ
    """

    model_config = ConfigDict(frozen=True)

    user: UserParams
    message: MessageParams


def load_params(path: Path = PARAMS_PATH) -> Params:
    """パラメタファイルを読み込んで検証する

    Args:
        path: パラメタファイルのパス

    Returns:
        検証済みのパラメタ

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        pydantic.ValidationError: 必須キーの欠落や値が不正な場合
    """
    return Params.model_validate_json(path.read_text(encoding="utf-8"))


# 起動時に一度だけ読み込むパラメタ（不正ならインポート時点でエラー）
params = load_params()
