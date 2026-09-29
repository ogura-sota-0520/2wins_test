import type { Room, Message, MessagePage, User } from "./types";

/** API がエラーを返したときの例外。message にはサーバの detail が入る。 */
export class ApiError extends Error {
  /** HTTP ステータスコード。 */
  readonly status: number;

  /**
   * @param status - HTTP ステータスコード。
   * @param message - 画面に表示するエラーメッセージ。
   */
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

type RequestOptions = {
  method?: "GET" | "POST";
  body?: unknown;
  /** 401 のときに /login へ遷移するか（ログイン・登録の 401 は画面にエラー表示するため false）。 */
  redirectOn401?: boolean;
};

/**
 * バックエンド API を呼び出す共通処理。
 *
 * @param path - /api を除いたパス。
 * @param options - {@link RequestOptions}
 * @returns レスポンスボディ（204 の場合は undefined）。
 * @throws {@link ApiError} レスポンスがエラーの場合。
 */
async function request<T>(
  path: string,
  { method = "GET", body, redirectOn401 = true }: RequestOptions = {},
): Promise<T> {
  // リクエスト送信
  const res = await fetch(`/api${path}`, {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  // セッション切れ時の /login 遷移（クライアント状態を確実に消すため router ではなくフルリロード）
  if (res.status === 401 && redirectOn401) {
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- 意図的な全画面リロード
    window.location.href = "/login";
  }
  // エラーと本文なしレスポンスの処理
  if (!res.ok) {
    throw new ApiError(res.status, await readErrorMessage(res));
  }
  // 204 No Content の場合は空のままではなく undefined を返す
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

/**
 * エラーレスポンスから表示用のメッセージを取り出す。
 *
 * @param res - エラーレスポンス。
 * @returns サーバの detail。文字列の detail がなければ既定のメッセージ。
 */
async function readErrorMessage(res: Response): Promise<string> {
  try {
    const data: unknown = await res.json();
    if (typeof data === "object" && data !== null && "detail" in data && typeof data.detail === "string") {
      return data.detail;
    }
  } catch {
    // JSON でないレスポンスは既定メッセージへ
  }
  return res.status === 422 ? "入力内容が正しくありません" : "エラーが発生しました";
}

type ListMessagesParams = {
  limit?: number;
  beforeId?: number;
  afterId?: number;
};

/** バックエンド API のクライアント。 */
export const api = {
  // 認証
  register: (name: string) =>
    request<User>("/auth/register", { method: "POST", body: { name }, redirectOn401: false }),
  login: (name: string) =>
    request<User>("/auth/login", { method: "POST", body: { name }, redirectOn401: false }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  me: () => request<User>("/auth/me"),

  // ルーム
  listRooms: () => request<Room[]>("/rooms"),
  createRoom: (partnerName: string) =>
    request<Room>("/rooms", { method: "POST", body: { partner_name: partnerName } }),
  getRoom: (id: number) => request<Room>(`/rooms/${id}`),

  // メッセージ
  listMessages: (roomId: number, { limit, beforeId, afterId }: ListMessagesParams = {}) => {
    const query = new URLSearchParams();
    if (limit !== undefined) query.set("limit", String(limit));
    if (beforeId !== undefined) query.set("before_id", String(beforeId));
    if (afterId !== undefined) query.set("after_id", String(afterId));
    const queryString = query.toString();
    const suffix = queryString ? `?${queryString}` : "";
    return request<MessagePage>(`/rooms/${roomId}/messages${suffix}`);
  },
  sendMessage: (roomId: number, body: string) =>
    request<Message>(`/rooms/${roomId}/messages`, { method: "POST", body: { body } }),
};
