"use client";

import { AuthForm } from "@/components/AuthForm";
import { api } from "@/lib/api";

/**
 * ログイン画面（/login）。
 *
 * @returns ログインフォーム。成功すると /chats へ遷移する。
 */
export default function LoginPage() {
  return (
    <AuthForm
      title="ログイン"
      submitLabel="ログイン"
      secondaryLabel="新規ユーザ登録"
      secondaryHref="/register"
      onSubmit={(name) => api.login(name)}
    />
  );
}
