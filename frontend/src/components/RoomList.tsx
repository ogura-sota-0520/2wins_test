"use client";

import Link from "next/link";
import { formatPartnerName } from "@/lib/format";
import { useMe } from "@/lib/me-context";
import type { Room } from "@/lib/types";

type Props = {
  /** 表示するルーム（最新メッセージ順）。 */
  rooms: Room[];
  /** 選択中のルーム id。未選択なら null。 */
  selectedRoomId: number | null;
};

/**
 * ルーム一覧。相手の名前と最新メッセージを表示する。
 *
 * @param props - {@link Props}
 * @returns ルームへのリンクの一覧。ルームがなければ案内文。
 */
export function RoomList({ rooms, selectedRoomId }: Props) {
  const me = useMe();

  // ルームなしの案内
  if (rooms.length === 0) {
    return <p className="p-3 text-sm text-gray-500">ルームがありません。ユーザ名を入力して追加してください</p>;
  }

  return (
    <ul className="flex-1 overflow-y-auto">
      {rooms.map((room) => (
        <li key={room.id}>
          <Link
            href={`/chats/${room.id}`}
            className={`block border-b border-gray-200 px-3 py-2 ${
              room.id === selectedRoomId ? "bg-gray-100" : "hover:bg-gray-50"
            }`}
          >
            <p className="font-bold">{formatPartnerName(room, me)}</p>
            <p className="truncate text-sm text-gray-500">
              {room.last_message?.body ?? "メッセージはまだありません"}
            </p>
          </Link>
        </li>
      ))}
    </ul>
  );
}
