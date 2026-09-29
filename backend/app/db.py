"""DB 接続（エンジン・セッション生成器）と全モデル共通の基底クラス Base の定義。"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 接続先（ローカルの SQLite ファイル）
_DATABASE_URL = "sqlite:///./chat.db"

# エンジン（SQLite ファイルとの接続管理）（FastAPI のスレッドプールから使うためスレッド制約を解除）
engine = create_engine(_DATABASE_URL, connect_args={"check_same_thread": False})

# リクエストごとにDB セッションを作る生成器
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """全モデル共通の基底クラス。

    これを継承したクラスは Base.metadata にテーブル定義が登録される。
    """


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """SQLite 接続ごとに外部キー制約を有効化する。

    SQLite は既定で外部キー制約を検査しないため、接続が張られるたびに PRAGMA を発行する。

    Args:
        dbapi_connection: DB-API レベルの生の接続。
        _connection_record: SQLAlchemy の接続レコード（未使用）。
    """
    # 外部キー制約の有効化
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
