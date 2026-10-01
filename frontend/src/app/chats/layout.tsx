"use client";

import { useEffect, useState, type ReactNode } from "react";
import { Sidebar } from "@/components/Sidebar";
import { api, ApiError } from "@/lib/api";
import { MeContext } from "@/lib/me-context";
import type { User } from "@/lib/types";

/**
 * チャット画面共通のレイアウト。ログイン中のユーザを取得し、サイドバーと並べて表示する。
 *
 * @param props.children - 右側に表示するページ。
 * @returns サイドバー付きのレイアウト。
 */
export default function ChatsLayout({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<User | null>(null);
  const [error, setError] = useState(false);

  // ログイン中ユーザ取得を初期に1度だけ実行（未ログインの 401 は api.ts が /login へ遷移）
  useEffect(() => {
    api
      .me()
      .then(setMe)
      .catch((err: unknown) => {
        if (!(err instanceof ApiError && err.status === 401)) {
          setError(true);
        }
      });
  }, []);

  // 接続エラー・読み込み中の表示
  if (error) {
    return <p className="p-4 text-gray-500">サーバに接続できません。時間をおいて再読み込みしてください</p>;
  }

  if (me === null) {
    return <p className="p-4 text-gray-500">読み込み中...</p>;
  }

  // MeContext に現在のユーザ情報 me を渡しておく
  return (
    <MeContext value={me}>
      <div className="flex h-screen">
        <Sidebar />
        <section className="min-w-0 flex-1">{children}</section>
      </div>
    </MeContext>
  );
}
