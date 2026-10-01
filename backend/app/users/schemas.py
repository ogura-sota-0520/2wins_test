"""ユーザ名の検証ルールとユーザ情報のレスポンス形式の定義。"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.config import params

# ユーザ名の入力制約（前後の空白を除いて 1〜name_max_length 文字）
UserName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=params.user.name_max_length),
]


class UserOut(BaseModel):
    """API で返すレスポンス形式のユーザ情報。

    Attributes:
        id: ユーザ id。
        name: ユーザ名。
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
