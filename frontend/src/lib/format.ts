import type { Room, User } from "./types";

/**
 * 日時を「時:分」形式にする。
 *
 * @param iso - ISO 8601 形式の日時。
 * @returns ブラウザのタイムゾーンでの "HH:mm"。
 */
export function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" });
}

/**
 * ルームの参加者のうち自分以外の名前を返す。
 *
 * @param room - ルーム。
 * @param me - ログイン中のユーザ。
 * @returns 相手の名前（複数ならカンマ区切り）。
 */
export function formatPartnerName(room: Room, me: User): string {
  return room.members
    .filter((member) => member.id !== me.id)
    .map((member) => member.name)
    .join(", ");
}
