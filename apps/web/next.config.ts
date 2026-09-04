import createNextIntlPlugin from 'next-intl/plugin';
import type { NextConfig } from 'next';

const withNextIntl = createNextIntlPlugin(
    './src/i18n.ts'
);

const nextConfig: NextConfig = {
  ...(process.env.DOCKER_BUILD === '1' ? { output: 'standalone' } : {}),
};

export default withNextIntl(nextConfig);
