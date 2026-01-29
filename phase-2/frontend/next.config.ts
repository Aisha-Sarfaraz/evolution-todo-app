import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Ignore TypeScript errors during build (strict tsconfig may fail on Vercel)
  typescript: {
    ignoreBuildErrors: true,
  },
  // Ignore ESLint errors during build
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
