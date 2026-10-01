import type { Message } from "./types";

/**
 * 2つのメッセージ列を id で重複を除いて結合する。
 *
 * @param current - 表示中のメッセージ。
 * @param incoming - 新たに取得したメッセージ。
 * @returns id 昇順に並べた結合結果。
 */
export function mergeMessages(current: Message[], incoming: Message[]): Message[] {
  const byId = new Map(current.map((message) => [message.id, message]));
  for (const message of incoming) {
    byId.set(message.id, message);
  }
  return [...byId.values()].sort((a, b) => a.id - b.id);
}
