"""認証 API で受け取るリクエスト（ユーザ名）の形式と検証ルールの定義。"""

from pydantic import BaseModel

from app.users.schemas import UserName


class Credentials(BaseModel):
    """登録・ログインのリクエストボディ．APIの入力検証に使用．

    Attributes:
        name: ユーザ名（前後の空白を除いて 1〜20 文字）。
    """

    name: UserName
