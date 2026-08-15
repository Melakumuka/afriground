"use client";

import Link from "next/link";
import AfriGroundTechnicalHUD, { type HudText } from "./AfriGroundTechnicalHUD";

export type HeroText = {
  eyebrow: string;
  titleA: string;
  titleB: string;
  subtitle: string;
  ctaNetwork: string;
  ctaTalk: string;
  scope: string;
  scopeValue: string;
} & HudText;

export default function CinematicHero({
  locale,
  text,
}: {
  locale: string;
  text: HeroText;
}) {
  return (
    <section className="relative z-10 min-h-screen flex flex-col text-ink overflow-hidden">
      {/* Editorial copy over the full-page orbital scene */}
      <div className="relative z-20 flex-1 flex items-center">
        {/* Left-to-right scrim keeps copy legible over the 3D scene */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-graphite/85 via-graphite/50 to-transparent" />

        <div className="relative w-full max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-24">
          <div className="max-w-xl">
            <div
              className="animate-fade-up inline-flex items-center gap-3 font-mono text-[11px] tracking-[0.18em] uppercase text-signal-soft mb-8"
              style={{ animationDelay: "0.1s" }}
            >
              <span className="w-8 h-px bg-signal" />
              {text.eyebrow}
            </div>

            <h1
              className="animate-fade-up font-display font-bold text-4xl sm:text-5xl lg:text-6xl xl:text-[4.25rem] leading-[1.04] tracking-tight text-white"
              style={{ animationDelay: "0.2s" }}
            >
              {text.titleA}
              <br />
              <span className="text-signal-soft">{text.titleB}</span>
            </h1>

            <p
              className="animate-fade-up mt-7 text-steel-2 text-base sm:text-lg leading-relaxed max-w-md"
              style={{ animationDelay: "0.3s" }}
            >
              {text.subtitle}
            </p>

            <div
              className="animate-fade-up mt-10 flex flex-col sm:flex-row gap-4"
              style={{ animationDelay: "0.4s" }}
            >
              <Link
                href={`/${locale}/booking`}
                className="px-7 py-3.5 bg-signal hover:bg-signal-soft text-graphite font-semibold text-sm tracking-wide transition-colors"
              >
                {text.ctaNetwork} →
              </Link>
              <Link
                href={`/${locale}/contact`}
                className="px-7 py-3.5 border border-graphite-600 hover:border-steel text-steel-2 hover:text-white text-sm font-semibold tracking-wide transition-colors"
              >
                {text.ctaTalk}
              </Link>
            </div>
          </div>
        </div>

        {/* Viewport label pinned over the scene */}
        <div className="absolute top-8 right-6 sm:right-10 lg:right-14 z-30 pointer-events-none">
          <div className="flex items-center gap-3 justify-end">
            <span className="px-2.5 py-1 border border-graphite-600 bg-graphite/80 font-mono text-[10px] uppercase tracking-widest text-steel-2">
              {text.scope}
            </span>
            <span className="font-mono text-[10px] text-graphite-mute uppercase tracking-widest">
              {text.scopeValue}
            </span>
          </div>
        </div>
      </div>

      {/* Telemetry strip */}
      <div className="relative z-30 px-6 sm:px-10 lg:px-14 pb-6 animate-fade-up">
        <AfriGroundTechnicalHUD text={text} />
      </div>
    </section>
  );
}