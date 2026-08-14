import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';
import fs from 'fs';
import path from 'path';

const locales = ['en', 'zh'];

export default getRequestConfig(async (params) => {
  const reqLocale = await params.requestLocale;
  const locale = reqLocale || (params as any)?.locale || 'en';

  const targetLocale = locales.includes(locale) ? locale : 'en';

  try {
    const filePath = path.resolve(process.cwd(), `messages/${targetLocale}.json`);
    const fileContent = fs.readFileSync(filePath, 'utf-8');
    const messages = JSON.parse(fileContent);
    return {
      locale: targetLocale,
      messages
    };
  } catch (error) {
    const fallbackPath = path.resolve(process.cwd(), `messages/en.json`);
    const fallbackContent = fs.readFileSync(fallbackPath, 'utf-8');
    return {
      locale: 'en',
      messages: JSON.parse(fallbackContent)
    };
  }
});
