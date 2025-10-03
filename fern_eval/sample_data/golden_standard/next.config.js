/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: false,
  },
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ["localhost"],
  },
};

module.exports = nextConfig;
