"use client";

import { useRouter } from "next/navigation";
import { AuthForm } from "@/components/AuthForm";
import { api } from "@/lib/api";

/**
 * 新規ユーザ登録画面（/register）。
 *
 * @returns 登録フォーム。成功するとログイン状態で /chats へ遷移する。
 */
export default function RegisterPage() {
  const router = useRouter();

  return (
    <AuthForm
      title="新規ユーザ登録"
      submitLabel="作成"
      secondaryLabel="ログイン画面へ戻る"
      secondaryHref="/login"
      onSubmit={async (name) => {
        await api.register(name);
        router.push("/chats");
      }}
    />
  );
}
