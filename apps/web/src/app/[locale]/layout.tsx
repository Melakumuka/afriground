import type { Metadata } from 'next';
import { Space_Grotesk, IBM_Plex_Mono } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import './globals.css';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  weight: ['400', '500', '600', '700'],
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  variable: '--font-ibm-plex-mono',
  weight: ['400', '500', '600'],
});

export const metadata: Metadata = {
  title: 'AfriGround GSaaS — Africa\'s Premier Ground Station Network',
  description: "Federated Ground Station as a Service platform for satellite pass scheduling, TT&C, and Earth observation downlinks across Africa.",
};

export default async function RootLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const { locale } = await params;
  const messages = await getMessages();

  return (
    <html lang={locale} className="dark">
      <body className={`${spaceGrotesk.variable} ${ibmPlexMono.variable} bg-graphite text-ink min-h-screen flex flex-col justify-between selection:bg-signal selection:text-graphite`}>
        <NextIntlClientProvider messages={messages}>
          <Navbar currentLocale={locale} />
          <div className="flex-1">
            {children}
          </div>
          <Footer currentLocale={locale} />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

