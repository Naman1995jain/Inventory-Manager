/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    API_URL: process.env.API_URL || 'http://localhost:8000/api/v1',
  },
  output: 'standalone',
  experimental: {
    outputFileTracingRoot: undefined,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'books.toscrape.com',
        port: '',
        pathname: '/media/cache/**',
      },
    ],
  },
}

module.exports = nextConfig