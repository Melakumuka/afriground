"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useMessages } from "next-intl";

export default function Navbar({ currentLocale }: { currentLocale: string }) {
  const pathname = usePathname();
  const router = useRouter();
  
  // Access raw messages object safely to prevent next-intl dev console error logging
  const messages = useMessages() as any;
  const nav = messages?.Navigation || {};

  const isZh = currentLocale === "zh";

  const navLinks = [
    { href: `/${currentLocale}`, label: nav.home || (isZh ? "首页" : "Home") },
    { href: `/${currentLocale}/booking`, label: nav.scheduling || (isZh ? "过境调度" : "Pass Scheduling") },
    { href: `/${currentLocale}/station`, label: nav.telemetry || (isZh ? "实时遥测" : "Live Telemetry") },
    { href: `/${currentLocale}/data`, label: nav.catalog || (isZh ? "数据下传" : "Data Catalog") },
    { href: `/${currentLocale}/support`, label: nav.support || (isZh ? "SLA & 支持" : "SLA & Support") },
  ];

  // Helper to switch locale
  const toggleLocale = () => {
    const nextLocale = isZh ? "en" : "zh";
    const newPath = pathname.replace(`/${currentLocale}`, `/${nextLocale}`);
    router.push(newPath || `/${nextLocale}`);
  };

  return (
    <header className="sticky top-0 z-50 w-full glass-panel border-b border-white/10 backdrop-blur-xl bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href={`/${currentLocale}`} className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <span className="text-xl">📡</span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xl font-black tracking-tight text-white font-mono">
                Afri<span className="text-cyan-400">Ground</span>
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded">
                GSaaS
              </span>
            </div>
            <p className="text-[10px] text-slate-400 tracking-wider uppercase font-semibold">
              Ground Station as a Service
            </p>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm"
                    : "text-slate-300 hover:text-white hover:bg-white/5"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Network Status & Actions */}
        <div className="flex items-center gap-4">
          {/* Live Node Pill */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs text-slate-300 shadow-inner">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-emerald-400 font-semibold">
              {nav.nodes_online || (isZh ? "14/14 网络节点在线" : "14/14 Network Nodes Online")}
            </span>
          </div>

          {/* Language Switcher */}
          <button
            onClick={toggleLocale}
            className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 text-xs font-mono tracking-wider transition-all cursor-pointer"
            title="Switch Language"
          >
            🌐 {currentLocale.toUpperCase()}
          </button>

          {/* Primary CTA */}
          <Link
            href={`/${currentLocale}/booking`}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-sm font-semibold shadow-lg shadow-cyan-500/25 transition-all hover:scale-105 active:scale-95"
          >
            {nav.schedule_pass || (isZh ? "预订过境" : "Schedule a Pass")}
          </Link>
        </div>

      </div>
    </header>
  );
}
