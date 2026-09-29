/** ユーザ。 */
export type User = {
  id: number;
  name: string;
};

/** メッセージ。created_at は UTC の ISO 8601（末尾 Z）。 */
export type Message = {
  id: number;
  room_id: number;
  sender_id: number;
  body: string;
  created_at: string;
};

/** ルーム。last_message はまだメッセージがなければ null。 */
export type Room = {
  id: number;
  members: User[];
  last_message: Message | null;
};

/** メッセージ一覧の1ページ分。 */
export type MessagePage = {
  messages: Message[];
  has_more: boolean;
};
