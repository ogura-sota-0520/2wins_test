import params from "../../../config/params.json";

/** リポジトリ直下の config/params.json の形式（バックエンドと共有） */
export type AppParams = {
  user: {
    /** ユーザ名の最大文字数 */
    nameMaxLength: number;
  };
  message: {
    /** 本文の最大文字数 */
    bodyMaxLength: number;
    /** 一覧取得の既定件数 */
    pageSize: number;
    /** 一覧取得で指定できる最大件数 */
    pageSizeMax: number;
  };
  polling: {
    /** ルーム一覧のポーリング間隔（ミリ秒） */
    roomsIntervalMs: number;
    /** 新着メッセージのポーリング間隔（ミリ秒） */
    messagesIntervalMs: number;
  };
  scroll: {
    /** 最上部からこの距離（px）未満で過去ログを読み込む */
    loadOlderThresholdPx: number;
    /** 最下部からこの距離（px）未満なら新着へ追従する */
    nearBottomThresholdPx: number;
  };
};

/** ビルド時に埋め込まれるアプリのパラメタ */
export const config: AppParams = params;
