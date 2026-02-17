/** @type {import('next').NextConfig} */
const nextConfig = {
	eslint: {
		// Unblock production builds even if there are ESLint errors
		ignoreDuringBuilds: true,
	},
	async rewrites() {
		// Use local backend if NEXT_PUBLIC_API_URL is set, otherwise use production
		const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://m4l-backend.onrender.com';
		
		return [
			{
				source: '/api/:path*',
				destination: `${apiUrl}/api/:path*`,
			},
			{
				source: '/downloads/:path*',
				destination: `${apiUrl}/downloads/:path*`,
			},
			{
				source: '/view/:path*',
				destination: `${apiUrl}/view/:path*`,
			},
		];
	},
};

export default nextConfig;
