"use client";

import { useParams } from "next/navigation";
import { ChatRoom } from "@/components/ChatRoom";

/**
 * チャットルーム画面（/chats/[id]）。
 *
 * @returns URL のルーム id に対応するチャットルーム。
 */
export default function ChatPage() {
  const params = useParams<{ id: string }>();
  const roomId = Number(params.id);
  // key 指定でルーム切り替え時に状態リセット
  return <ChatRoom key={roomId} roomId={roomId} />;
}
