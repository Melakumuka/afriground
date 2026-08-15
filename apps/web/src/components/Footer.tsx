"use client";

import Link from "next/link";
import { useMessages } from "next-intl";

function DishMark() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M2.5 19.5a12 12 0 0 1 19 0" stroke="#15171A" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M12 19.5V7M12 7l-3.4 3.6M12 7l3.4 3.6M12 4v3" stroke="#15171A" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="12" cy="19.5" r="1.3" fill="#15171A" />
    </svg>
  );
}

export default function Footer({ currentLocale }: { currentLocale: string }) {
  const messages = useMessages() as Record<string, Record<string, string>>;
  const nav = messages?.Navigation || {};
  const isZh = currentLocale === "zh";

  return (
    <footer className="w-full bg-graphite border-t border-graphite-600/60 text-graphite-mute text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          
          {/* Col 1: Brand & Tagline */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-signal flex items-center justify-center">
                <DishMark />
              </div>
              <span className="text-xl font-black text-white font-display tracking-tight">
                Afri<span className="text-signal-soft">Ground</span>
              </span>
            </div>
            
            <p className="text-graphite-mute text-sm leading-relaxed max-w-sm">
              Africa&apos;s premier multi-ground-station aggregator and Ground Station as a Service (GSaaS) platform for satellite pass scheduling, TT&C, and Earth observation downlinks.
            </p>

            <div className="flex items-center gap-3 pt-2">
              <span className="px-2.5 py-1 text-xs border border-graphite-600 text-steel-2 font-mono">
                CCSDS Compliant
              </span>
              <span className="px-2.5 py-1 text-xs border border-graphite-600 text-steel-2 font-mono">
                ITU Band Cleared
              </span>
              <span className="px-2.5 py-1 text-xs border border-green/40 text-green-soft font-mono">
                ISO 27001
              </span>
            </div>
          </div>

          {/* Col 2: Platform Modules */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              GSaaS Modules
            </h4>
            <ul className="space-y-2.5 text-graphite-mute">
              <li>
                <Link href={`/${currentLocale}/booking`} className="hover:text-signal-soft transition-colors">
                  {nav.scheduling || (isZh ? "过境调度" : "Pass Scheduling")} & Quote
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/station`} className="hover:text-signal-soft transition-colors">
                  {nav.telemetry || (isZh ? "实时遥测" : "Live Telemetry")} & Risk
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/data`} className="hover:text-signal-soft transition-colors">
                  {nav.catalog || (isZh ? "数据下传" : "Data Catalog")}
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/support`} className="hover:text-signal-soft transition-colors">
                  {nav.support || (isZh ? "SLA & 支持" : "SLA & Support")}
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Key Ground Stations */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              Station Network Hubs
            </h4>
            <ul className="space-y-2.5 text-graphite-mute font-mono text-xs">
              <li>Entoto Observatory</li>
              <li>Hartebeesthoek</li>
              <li>Malindi Terminal</li>
              <li>Abuja Hub</li>
              <li>Cairo Gateway</li>
              <li>Dakar Atlantic</li>
            </ul>
          </div>

          {/* Col 4: Operations & Contact */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              Space Ops Desk
            </h4>
            <div className="space-y-3 text-graphite-mute text-xs font-mono">
              <p>Entoto Space Institute, Addis Ababa, Ethiopia</p>
              <p>ops@afriground.space</p>
              <p>24/7 Hotline: +251 (0) 11 896 1234</p>
              <div className="pt-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 border border-green/40 text-green-soft text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-soft animate-ping" />
                  Telemetry Feeds Live
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-graphite-600/50 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-graphite-mute font-mono">
          <p>© {new Date().getFullYear()} AfriGround GSaaS Platform. All rights reserved.</p>
          <div className="flex gap-6">
            <span className="hover:text-steel-2 cursor-pointer">Privacy Policy</span>
            <span className="hover:text-steel-2 cursor-pointer">Terms of Service</span>
            <span className="hover:text-steel-2 cursor-pointer">API Reference</span>
          </div>
        </div>

      </div>
    </footer>
  );
}