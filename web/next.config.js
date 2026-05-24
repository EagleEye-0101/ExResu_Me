const path = require("path");

/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: path.join(__dirname),
  transpilePackages: ["monaco-editor"],
  webpack: (config, { isServer }) => {
    if (isServer) {
      const existing = config.externals;
      if (Array.isArray(existing)) {
        config.externals = [...existing, "monaco-editor"];
      } else if (existing) {
        config.externals = [existing, "monaco-editor"];
      } else {
        config.externals = ["monaco-editor"];
      }
    }
    return config;
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
