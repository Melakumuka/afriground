"use client";

import Link from "next/link";
import { useMessages } from "next-intl";

export default function Footer({ currentLocale }: { currentLocale: string }) {
  const messages = useMessages() as any;
  const nav = messages?.Navigation || {};
  const isZh = currentLocale === "zh";

  return (
    <footer className="w-full bg-slate-950 border-t border-slate-800/80 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          
          {/* Col 1: Brand & Tagline */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <span className="text-lg">📡</span>
              </div>
              <span className="text-xl font-black text-white font-mono tracking-tight">
                Afri<span className="text-cyan-400">Ground</span>
              </span>
            </div>
            
            <p className="text-slate-400 text-sm leading-relaxed max-w-sm">
              Africa&apos;s premier multi-ground-station aggregator and Ground Station as a Service (GSaaS) platform for satellite pass scheduling, TT&C, and Earth observation downlinks.
            </p>

            <div className="flex items-center gap-3 pt-2">
              <span className="px-2.5 py-1 text-xs rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono">
                CCSDS Compliant
              </span>
              <span className="px-2.5 py-1 text-xs rounded bg-slate-900 border border-slate-800 text-slate-300 font-mono">
                ITU Band Cleared
              </span>
              <span className="px-2.5 py-1 text-xs rounded bg-slate-900 border border-slate-800 text-emerald-400 font-mono">
                ISO 27001
              </span>
            </div>
          </div>

          {/* Col 2: Platform Modules */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              GSaaS Modules
            </h4>
            <ul className="space-y-2.5 text-slate-400">
              <li>
                <Link href={`/${currentLocale}/booking`} className="hover:text-cyan-400 transition-colors">
                  {nav.scheduling || (isZh ? "过境调度" : "Pass Scheduling")} & Quote
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/station`} className="hover:text-cyan-400 transition-colors">
                  {nav.telemetry || (isZh ? "实时遥测" : "Live Telemetry")} & Risk
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/data`} className="hover:text-cyan-400 transition-colors">
                  {nav.catalog || (isZh ? "数据下传" : "Data Catalog")}
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/support`} className="hover:text-cyan-400 transition-colors">
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
            <ul className="space-y-2.5 text-slate-400 font-mono text-xs">
              <li className="flex justify-between items-center">
                <span>Entoto Observatory</span>
                <span className="text-cyan-400">12.0m X/S</span>
              </li>
              <li className="flex justify-between items-center">
                <span>Hartebeesthoek</span>
                <span className="text-cyan-400">9.3m Ka/X</span>
              </li>
              <li className="flex justify-between items-center">
                <span>Malindi Terminal</span>
                <span className="text-cyan-400">10.0m S-band</span>
              </li>
              <li className="flex justify-between items-center">
                <span>Abuja Hub</span>
                <span className="text-cyan-400">7.3m S/X</span>
              </li>
              <li className="flex justify-between items-center">
                <span>Cairo Gateway</span>
                <span className="text-cyan-400">11.2m X-band</span>
              </li>
              <li className="flex justify-between items-center">
                <span>Dakar Atlantic</span>
                <span className="text-cyan-400">5.5m S/UHF</span>
              </li>
            </ul>
          </div>

          {/* Col 4: Operations & Contact */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              Space Ops Desk
            </h4>
            <div className="space-y-3 text-slate-400 text-xs font-mono">
              <p>📍 Entoto Space Institute, Addis Ababa, Ethiopia</p>
              <p>✉️ ops@afriground.space</p>
              <p>⚡ 24/7 Hotline: +251 (0) 11 896 1234</p>
              <div className="pt-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  Telemetry Feeds Live
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 font-mono">
          <p>© {new Date().getFullYear()} AfriGround GSaaS Platform. All rights reserved.</p>
          <div className="flex gap-6">
            <span className="hover:text-slate-400 cursor-pointer">Privacy Policy</span>
            <span className="hover:text-slate-400 cursor-pointer">Terms of Service</span>
            <span className="hover:text-slate-400 cursor-pointer">API Reference</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
