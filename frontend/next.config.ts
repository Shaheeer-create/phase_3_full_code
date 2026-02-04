import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output for Docker containerization
  output: 'standalone',
  // Removed trailingSlash: true to fix Better Auth routing
};

export default nextConfig;
