import { getRequestConfig } from 'next-intl/server';

const locales = ['en', 'zh'];

export default getRequestConfig(async (params) => {
  const reqLocale = await params.requestLocale;
  const locale = reqLocale || 'en';
  const targetLocale = locales.includes(locale) ? locale : 'en';

  try {
    const messages = (await import(`../messages/${targetLocale}.json`)).default;
    return {
      locale: targetLocale,
      messages
    };
  } catch {
    const fallbackMessages = (await import(`../messages/en.json`)).default;
    return {
      locale: 'en',
      messages: fallbackMessages
    };
  }
});
