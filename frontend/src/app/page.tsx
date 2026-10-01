import { redirect } from "next/navigation";

/**
 * トップページ（/）。/chats へリダイレクトする。
 */
export default function HomePage() {
  // 未ログイン時は /chats 側で /login へ遷移
  redirect("/chats");
}
