"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { MessageForm } from "./MessageForm";
import { MessageList } from "./MessageList";
import { ApiError, api } from "@/lib/api";
import { formatPartnerName } from "@/lib/format";
import { useMe } from "@/lib/me-context";
import { mergeMessages } from "@/lib/messages";
import type { Room, Message } from "@/lib/types";
import { usePolling } from "@/lib/usePolling";

const PAGE_SIZE = 50;
const MESSAGES_POLL_INTERVAL_MS = 2000;
const LOAD_OLDER_THRESHOLD_PX = 40;
const NEAR_BOTTOM_THRESHOLD_PX = 80;

/** メッセージ一覧を更新した直後に行うスクロール。 */
type PendingScroll =
  | { type: "bottom" }
  | { type: "keep"; prevScrollHeight: number; prevScrollTop: number };

/**
 * スクロール位置が最下部付近かを判定する。
 *
 * @param el - メッセージ一覧のコンテナ。
 * @returns 最下部から NEAR_BOTTOM_THRESHOLD_PX 未満なら true。
 */
function isNearBottom(el: HTMLElement | null): boolean {
  return el !== null && el.scrollHeight - el.scrollTop - el.clientHeight < NEAR_BOTTOM_THRESHOLD_PX;
}

/**
 * チャットルーム。メッセージの初回取得・新着のポーリング・過去ログ読み込み・送信を扱う。
 *
 * @param props.roomId - 表示するルーム id。
 * @returns ヘッダ・メッセージ一覧・送信フォーム。
 */
export function ChatRoom({ roomId }: { roomId: number }) {
  const me = useMe();
  const [room, setRoom] = useState<Room | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [hasOlder, setHasOlder] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  // ポーリングや過去ログ読み込みから常に最新の一覧を参照するための、state と同じ値の ref
  const messagesRef = useRef<Message[]>([]);
  const loadedRef = useRef(false);
  const loadingOlderRef = useRef(false);
  const pendingScrollRef = useRef<PendingScroll | null>(null);

  // 取得したメッセージの一覧への統合（ref と state の両方を更新）
  const applyMessages = useCallback((incoming: Message[]) => {
    const next = mergeMessages(messagesRef.current, incoming);
    messagesRef.current = next;
    setMessages(next);
  }, []);

  // 初回表示: ルーム情報と最新 PAGE_SIZE 件
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [fetchedRoom, page] = await Promise.all([
          api.getRoom(roomId),
          api.listMessages(roomId, { limit: PAGE_SIZE }),
        ]);
        if (cancelled) return;
        pendingScrollRef.current = { type: "bottom" };
        setRoom(fetchedRoom);
        setHasOlder(page.has_more);
        applyMessages(page.messages);
        loadedRef.current = true;
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "読み込みに失敗しました");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [roomId, applyMessages]);

  // 一覧の描画直後のスクロール位置調整
  useLayoutEffect(() => {
    const el = containerRef.current;
    const pending = pendingScrollRef.current;
    if (el === null || pending === null) return;
    el.scrollTop =
      pending.type === "bottom"
        ? el.scrollHeight
        : el.scrollHeight - pending.prevScrollHeight + pending.prevScrollTop;
    pendingScrollRef.current = null;
  }, [messages]);

  // 新着: 表示中の最新 id より後を取得、has_more の間は続けて取得
  const pollNewer = useCallback(async () => {
    if (!loadedRef.current) return;
    let afterId = messagesRef.current.at(-1)?.id ?? 0;
    let hasMore = true;
    while (hasMore) {
      const page = await api.listMessages(roomId, { afterId, limit: PAGE_SIZE });
      if (page.messages.length === 0) return;
      // 最下部付近を見ているときだけ新着へ追従
      if (isNearBottom(containerRef.current)) {
        pendingScrollRef.current = { type: "bottom" };
      }
      applyMessages(page.messages);
      afterId = page.messages[page.messages.length - 1].id;
      hasMore = page.has_more;
    }
  }, [roomId, applyMessages]);

  usePolling(pollNewer, MESSAGES_POLL_INTERVAL_MS);

  // 過去ログ: 表示中の最古 id より前を取得
  async function loadOlder() {
    const el = containerRef.current;
    const oldest = messagesRef.current[0];
    if (el === null || oldest === undefined || !hasOlder || loadingOlderRef.current) return;
    loadingOlderRef.current = true;
    try {
      const page = await api.listMessages(roomId, { beforeId: oldest.id, limit: PAGE_SIZE });
      // 先頭に追加しても、今見ているメッセージの位置を維持
      pendingScrollRef.current = {
        type: "keep",
        prevScrollHeight: el.scrollHeight,
        prevScrollTop: el.scrollTop,
      };
      setHasOlder(page.has_more);
      applyMessages(page.messages);
    } catch {
      // 失敗時は次のスクロールで再試行
    } finally {
      loadingOlderRef.current = false;
    }
  }

  // 最上部付近までのスクロールで過去ログ読み込み
  function handleScroll() {
    const el = containerRef.current;
    if (el !== null && el.scrollTop < LOAD_OLDER_THRESHOLD_PX) {
      void loadOlder();
    }
  }

  // 送信後は自分のメッセージを即時表示し、最下部へ
  async function handleSend(body: string) {
    const message = await api.sendMessage(roomId, body);
    pendingScrollRef.current = { type: "bottom" };
    applyMessages([message]);
  }

  // エラー・読み込み中の表示
  if (error !== null) {
    return <div className="flex h-full items-center justify-center bg-sky-100 text-red-600">{error}</div>;
  }
  if (room === null) {
    return <div className="flex h-full items-center justify-center bg-sky-100 text-gray-500">読み込み中...</div>;
  }

  return (
    <div className="flex h-full flex-col bg-sky-100">
      <header className="border-b border-black bg-white px-4 py-3 font-bold">
        {formatPartnerName(room, me)}
      </header>
      <MessageList messages={messages} meId={me.id} containerRef={containerRef} onScroll={handleScroll} />
      <MessageForm onSend={handleSend} />
    </div>
  );
}
