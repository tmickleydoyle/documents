/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: false,
  },
  images: {
    domains: ["localhost", "example.com"],
  },
  env: {
    CUSTOM_KEY: "value",
  },
};

module.exports = nextConfig;
