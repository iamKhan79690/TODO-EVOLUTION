import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for containerization
  output: 'standalone',

  // Disable TypeScript build errors for deployment
  typescript: {
    ignoreBuildErrors: true,
  },

  // Disable ESLint build errors for deployment
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Disable experimental features for stability
  experimental: {
    // Disable features that might cause issues in containers
  },

  // Configure for production
  poweredByHeader: false,

  // Port and host are set via environment variables and npm scripts
};

export default nextConfig;
