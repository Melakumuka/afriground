"use client";

import { useLocale, useMessages } from "next-intl";

export function useT(namespace: string) {
  const isZh = useLocale() === "zh";
  const msgs = useMessages() as Record<string, Record<string, unknown>>;
  const ns = (msgs?.[namespace] ?? {}) as Record<string, unknown>;

  const t = (key: string, zh: string, en: string): string => {
    const v = ns[key];
    if (typeof v === "string" && v) return v;
    return isZh ? zh : en;
  };

  return { t, isZh, ns };
}