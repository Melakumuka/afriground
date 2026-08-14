import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import './globals.css';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const inter = Inter({ subsets: ['latin'] });

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
      <body className={`${inter.className} bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between selection:bg-cyan-500 selection:text-slate-950`}>
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

