"use client";

import { createContext, useContext } from "react";
import type { User } from "./types";

/** ログイン中のユーザを配下のコンポーネントへ渡すコンテキスト。 */
export const MeContext = createContext<User | null>(null);

/**
 * ログイン中のユーザを取得する。
 *
 * @returns ログイン中のユーザ。
 * @throws Error MeContext の外側で呼んだ場合。
 */
export function useMe(): User {
  const me = useContext(MeContext);
  if (me === null) {
    throw new Error("useMe は MeContext の内側で使ってください");
  }
  return me;
}
