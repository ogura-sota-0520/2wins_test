"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type SubmitEvent } from "react";
import { ApiError } from "@/lib/api";
import { config } from "@/lib/config";

type Props = {
  /** フォームの見出し。 */
  title: string;
  /** 送信ボタンの文言。 */
  submitLabel: string;
  /** 入力されたユーザ名での送信処理。失敗時は ApiError を投げる。 */
  onSubmit: (name: string) => Promise<unknown>;
  /** もう一方の画面へのリンクの文言。 */
  secondaryLabel: string;
  /** もう一方の画面へのリンク先。 */
  secondaryHref: string;
};

/**
 * ログイン・登録で共通のユーザ名入力フォーム。
 *
 * @param props - {@link Props}
 * @returns 入力欄・送信ボタン・画面切り替えリンク。成功すると /chats へ遷移し、失敗時はエラーを表示する。
 */
export function AuthForm({ title, submitLabel, onSubmit, secondaryLabel, secondaryHref }: Props) {
  const router = useRouter();
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
    // 送信とチャット画面への遷移、失敗時のエラー表示（成功時は画面遷移のため送信中のまま）
    try {
      await onSubmit(trimmed);
      router.push("/chats");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "通信に失敗しました");
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-white">
      <form
        onSubmit={handleSubmit}
        className="flex w-80 flex-col gap-4 rounded-lg border border-black bg-white p-6"
      >
        <h1 className="text-center text-xl font-bold">{title}</h1>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={`ユーザ名（${config.user.nameMaxLength}文字以内）`}
          autoFocus
          className="rounded border border-black px-3 py-2"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={!canSubmit}
          className="rounded bg-[#06C755] py-2 font-bold text-white disabled:opacity-50"
        >
          {submitLabel}
        </button>
        <Link
          href={secondaryHref}
          className="rounded border border-black bg-white py-2 text-center text-black"
        >
          {secondaryLabel}
        </Link>
      </form>
    </main>
  );
}
