"use client";

import { useState, type SubmitEvent } from "react";
import { ApiError } from "@/lib/api";
import { config } from "@/lib/config";

type Props = {
  /** 入力されたユーザ名でルームを追加する処理。失敗時は ApiError を投げる。 */
  onAdd: (partnerName: string) => Promise<void>;
};

/**
 * ユーザ名を入力して相手を追加するフォーム。
 *
 * @param props - {@link Props}
 * @returns 入力欄と追加ボタン。失敗時はエラーを表示する。
 */
export function AddRoomForm({ onAdd }: Props) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // 送信可否の判定
  const trimmed = name.trim();
  const canSubmit = trimmed.length > 0 && trimmed.length <= config.user.nameMaxLength && !submitting;

  async function handleSubmit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    // 追加処理と、成功時の入力クリア・失敗時のエラー表示
    try {
      await onAdd(trimmed);
      setName("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "通信に失敗しました");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-b border-black p-3">
      <div className="flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="ユーザ名で追加"
          className="min-w-0 flex-1 rounded border border-black px-2 py-1"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          className="rounded bg-[#06C755] px-3 py-1 font-bold text-white disabled:opacity-50"
        >
          追加
        </button>
      </div>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </form>
  );
}
