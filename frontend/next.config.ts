import type { NextConfig } from "next";

// 転送先の FastAPI のオリジン
const apiOrigin = "http://localhost:8000";

const nextConfig: NextConfig = {
  // ブラウザからは同一オリジンの /api/* を呼び、Next.js が FastAPI へ転送（cookie を扱いやすくするため）
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiOrigin}/api/:path*` }];
  },
};

export default nextConfig;
