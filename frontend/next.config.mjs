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
				destination: 'https://m4l-backend.onrender.com/api/:path*',
			},
			{
				source: '/downloads/:path*',
				destination: 'https://m4l-backend.onrender.com/downloads/:path*',
			},
		];
	},
};

export default nextConfig;
