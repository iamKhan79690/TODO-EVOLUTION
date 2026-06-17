import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },

  turbopack: {
    root: "D:/code/Personal Projects/TODO-EVOLUTION",
  },

  poweredByHeader: false,
};

export default nextConfig;
