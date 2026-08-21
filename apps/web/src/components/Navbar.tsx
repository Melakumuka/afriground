"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useMessages } from "next-intl";

export default function Navbar({ currentLocale }: { currentLocale: string }) {
  const pathname = usePathname();
  const router = useRouter();
  
  // Access raw messages object safely to prevent next-intl dev console error logging
  const messages = useMessages() as Record<string, Record<string, string>>;
  const nav = messages?.Navigation || {};

  const isZh = currentLocale === "zh";

  const navLinks = [
    { href: `/${currentLocale}/booking`, label: nav.scheduling || (isZh ? "过境调度" : "Pass Scheduling") },
    // { href: `/${currentLocale}/station`, label: nav.telemetry || (isZh ? "实时遥测" : "Live Telemetry") },
    { href: `/${currentLocale}/commercial/quotes`, label: nav.commercial || (isZh ? "商务与计费" : "Commercial & Billing") },
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
    <header className="sticky top-0 z-50 w-full bg-graphite/90 backdrop-blur-xl border-b border-graphite-600/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href={`/${currentLocale}`} className="flex items-center gap-3 group">
          <div className="w-10 h-10 bg-signal flex items-center justify-center group-hover:scale-105 transition-transform">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M2.5 19.5a12 12 0 0 1 19 0" stroke="#15171A" strokeWidth="1.6" strokeLinecap="round" />
              <path d="M12 19.5V7M12 7l-3.4 3.6M12 7l3.4 3.6M12 4v3" stroke="#15171A" strokeWidth="1.6" strokeLinecap="round" />
              <circle cx="12" cy="19.5" r="1.3" fill="#15171A" />
            </svg>
          </div>
          <div>
            <span className="text-xl font-black tracking-tight text-white font-display">
              Afri<span className="text-signal-soft">Ground</span>
            </span>
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
                className={`px-4 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-signal/10 text-signal-soft border border-signal/30"
                    : "text-steel-2 hover:text-white hover:bg-white/5"
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
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 border border-graphite-600 text-xs text-steel-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-soft opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-soft"></span>
            </span>
            <span className="font-mono text-green-soft font-semibold">
              {nav.nodes_online || (isZh ? "14/14 网络节点在线" : "14/14 Network Nodes Online")}
            </span>
          </div>

          {/* Language Switcher */}
          <button
            onClick={toggleLocale}
            className="px-3 py-1.5 border border-graphite-600 text-steel-2 hover:text-white hover:border-graphite-500 text-xs font-mono tracking-wider transition-all cursor-pointer"
            title={isZh ? "切换语言" : "Switch Language"}
          >
            {currentLocale.toUpperCase()}
          </button>

          {/* Primary CTA */}
          <Link
            href={`/${currentLocale}/booking`}
            className="px-4 py-2 bg-signal hover:bg-signal-soft text-graphite text-sm font-semibold shadow-lg shadow-black/30 transition-all hover:scale-105 active:scale-95"
          >
            {nav.schedule_pass || (isZh ? "预订过境" : "Schedule a Pass")}
          </Link>
        </div>

      </div>
    </header>
  );
}
