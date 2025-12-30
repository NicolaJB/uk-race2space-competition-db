import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/query/:path*',
        destination: 'http://127.0.0.1:8000/query/:path*',
      },
      {
        source: '/team-insights/:path*',
        destination: 'http://127.0.0.1:8000/team-insights/:path*',
      },
    ];
  },
};

export default nextConfig;
