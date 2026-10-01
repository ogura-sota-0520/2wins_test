"use client";

import { useParams, useRouter } from "next/navigation";
import { useCallback, useState } from "react";
import { AddRoomForm } from "./AddRoomForm";
import { RoomList } from "./RoomList";
import { api } from "@/lib/api";
import { config } from "@/lib/config";
import { useMe } from "@/lib/me-context";
import type { Room } from "@/lib/types";
import { usePolling } from "@/lib/usePolling";

/**
 * サイドバー。ログイン中のユーザ名・ログアウト・ルームの追加・ルーム一覧を表示する。
 * ルーム追加後は /chats/[id]、ログアウト後は /login へ遷移する。
 *
 * @returns サイドバー。
 */
export function Sidebar() {
  const router = useRouter();
  const me = useMe();
  // 選択中のルーム id（/chats では id なし）
  const params = useParams<{ id: string }>();
  const selectedRoomId = params.id ? Number(params.id) : null;
  const [rooms, setRooms] = useState<Room[]>([]);

  // ルーム一覧の定期更新
  const refreshRooms = useCallback(async () => {
    setRooms(await api.listRooms());
  }, []);

  usePolling(refreshRooms, config.polling.roomsIntervalMs);

  // ルームの追加と、追加したルームへの遷移
  async function handleAdd(partnerName: string) {
    const room = await api.createRoom(partnerName);
    await refreshRooms();
    router.push(`/chats/${room.id}`);
  }

  // ログアウト（失敗してもログイン画面へ遷移）
  async function handleLogout() {
    try {
      await api.logout();
    } finally {
      router.push("/login");
    }
  }

  return (
    <aside className="flex w-72 shrink-0 flex-col border-r border-black bg-white">
      <header className="flex items-center justify-between border-b border-black p-3">
        <span className="truncate font-bold">{me.name}</span>
        <button onClick={handleLogout} className="rounded border border-black px-2 py-1 text-sm">
          ログアウト
        </button>
      </header>
      <AddRoomForm onAdd={handleAdd} />
      <RoomList rooms={rooms} selectedRoomId={selectedRoomId} />
    </aside>
  );
}
