/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  basePath: '/gestaobr',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || '/gestaobr/api'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
