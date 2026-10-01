"use client";

import { useState, type SubmitEvent } from "react";
import { ApiError } from "@/lib/api";

const MAX_BODY_LENGTH = 1000;

type Props = {
  /** 入力された本文の送信処理。失敗時は ApiError を投げる。 */
  onSend: (body: string) => Promise<void>;
};

/**
 * メッセージ送信フォーム。
 *
 * @param props - {@link Props}
 * @returns 入力欄と送信ボタン。失敗時はエラーを表示する。
 */
export function MessageForm({ onSend }: Props) {
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  // 送信可否の判定
  const trimmed = body.trim();
  const canSend = trimmed.length > 0 && trimmed.length <= MAX_BODY_LENGTH && !sending;

  async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!canSend) return;
    setSending(true);
    setError(null);
    // 送信と、成功時の入力クリア・失敗時のエラー表示
    try {
      await onSend(trimmed);
      setBody("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "送信に失敗しました");
    } finally {
      setSending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-black bg-sky-100 p-3">
      {error && <p className="mb-1 text-sm text-red-600">{error}</p>}
      <div className="flex gap-2">
        <input
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="メッセージを入力"
          className="min-w-0 flex-1 rounded border border-black bg-white px-3 py-2"
        />
        <button
          type="submit"
          disabled={!canSend}
          className="rounded bg-[#06C755] px-4 py-2 font-bold text-white disabled:opacity-50"
        >
          送信
        </button>
      </div>
    </form>
  );
}
