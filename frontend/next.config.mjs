/** @type {import('next').NextConfig} */
const nextConfig = {
	eslint: {
		// Unblock production builds even if there are ESLint errors
		ignoreDuringBuilds: true,
	},
	async rewrites() {
		return [
			{
				source: '/api/:path*',
				destination: 'http://127.0.0.1:8002/api/:path*',
			},
			{
				source: '/downloads/:path*',
				destination: 'http://127.0.0.1:8002/downloads/:path*',
			},
		];
	},
};

export default nextConfig;
