import path from "node:path";
import type { NextConfig } from "next";

// 転送先の FastAPI のオリジン
const apiOrigin = "http://localhost:8000";

const nextConfig: NextConfig = {
  // リポジトリ直下の config/params.json を import するため、解決範囲をリポジトリ直下まで拡大
  turbopack: {
    root: path.join(__dirname, ".."),
  },
  // ブラウザからは同一オリジンの /api/* を呼び、Next.js が FastAPI へ転送（cookie を扱いやすくするため）
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiOrigin}/api/:path*` }];
  },
};

export default nextConfig;
