"use client";

import type { Ref } from "react";
import { formatTime } from "@/lib/format";
import type { Message } from "@/lib/types";

type Props = {
  /** 表示するメッセージ（id 昇順）。 */
  messages: Message[];
  /** ログイン中のユーザ id。自分のメッセージを右寄せにするために使う。 */
  meId: number;
  /** スクロール位置を制御するためのコンテナ参照。 */
  containerRef: Ref<HTMLDivElement>;
  /** スクロール時の処理（過去ログ読み込みの判定）。 */
  onScroll: () => void;
};

/**
 * メッセージ一覧。自分のメッセージは右、相手のメッセージは左に吹き出しで表示する。
 *
 * @param props - {@link Props}
 * @returns スクロール可能なメッセージ一覧。
 */
export function MessageList({ messages, meId, containerRef, onScroll }: Props) {
  return (
    <div ref={containerRef} onScroll={onScroll} className="flex-1 overflow-y-auto px-4 py-3">
      {/* メッセージなしの案内 */}
      {messages.length === 0 && (
        <p className="py-8 text-center text-sm text-gray-500">まだメッセージはありません</p>
      )}
      {/* 吹き出しと送信時刻 */}
      <ul className="flex flex-col gap-2">
        {messages.map((message) => {
          const mine = message.sender_id === meId;
          return (
            <li key={message.id} className={`flex items-end gap-1 ${mine ? "flex-row-reverse" : ""}`}>
              <p
                className={`max-w-[70%] whitespace-pre-wrap break-words rounded-2xl px-3 py-2 ${
                  mine ? "bg-green-200" : "bg-gray-200"
                }`}
              >
                {message.body}
              </p>
              <time dateTime={message.created_at} className="text-xs text-gray-500">
                {formatTime(message.created_at)}
              </time>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
