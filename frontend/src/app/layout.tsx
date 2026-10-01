import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Simple Chat",
  description: "LINE風の簡易チャットアプリ",
};

/**
 * 全ページ共通のルートレイアウト。
 *
 * @param props.children - 表示するページ。
 * @returns html と body で包んだページ。
 */
export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ja">
      <body className="bg-white text-black antialiased">{children}</body>
    </html>
  );
}
