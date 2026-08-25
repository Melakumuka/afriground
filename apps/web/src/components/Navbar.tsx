"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useMessages } from "next-intl";
import { useState } from "react";

export default function Navbar({ currentLocale }: { currentLocale: string }) {
  const pathname = usePathname();
  const router = useRouter();
  
  // Access raw messages object safely to prevent next-intl dev console error logging
  const messages = useMessages() as Record<string, Record<string, string>>;
  const nav = messages?.Navigation || {};

  const isZh = currentLocale === "zh";

  const navLinks = [
    { href: `/${currentLocale}/booking`, label: nav.scheduling || (isZh ? "过境调度" : "Pass Scheduling") },
    { href: `/${currentLocale}/commercial/quotes`, label: nav.commercial || (isZh ? "商务与计费" : "Commercial & Billing") },
    { href: `/${currentLocale}/data`, label: nav.catalog || (isZh ? "数据下传" : "Data Catalog") },
    { href: `/${currentLocale}/data/egress`, label: nav.egress || (isZh ? "数据出口配置" : "Egress Config") },
    { href: `/${currentLocale}/missions/new`, label: nav.missions_new || (isZh ? "卫星注册" : "Register Satellite") },
    { href: `/${currentLocale}/station/new`, label: nav.station_new || (isZh ? "地面站注册" : "Register Station") },
    { href: `/${currentLocale}/support`, label: nav.support || (isZh ? "SLA & 支持" : "SLA & Support") },
  ];

  // Helper to switch locale
  const toggleLocale = () => {
    const nextLocale = isZh ? "en" : "zh";
    const newPath = pathname.replace(`/${currentLocale}`, `/${nextLocale}`);
    router.push(newPath || `/${nextLocale}`);
  };

  // Mobile menu state
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

        {/* Mobile Menu Button (hidden on md+) */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="xl:hidden p-2 rounded-md hover:bg-graphite-500 transition-colors"
          aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 12l2-2m0 0l7-7m7 7l2 2m0 0l7 7m7-7v2m-2 0h2"/>
            <path d="M19 12l2 2m0 0l-7 7m-7-7l2-2m0 0l-7-7"/>
          </svg>
        </button>

        {/* Desktop Navigation Links */}
        <nav className="hidden xl:flex items-center gap-1">
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

        {/* Mobile Menu (overlay, shown only on mobile) */}
        {mobileMenuOpen && (
          <nav className="fixed inset-0 bg-graphite/90 top-20 z-40 flex flex-col items-center gap-4 p-8 xl:hidden">
            {navLinks.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`text-2xl font-bold text-white transition-colors ${
                    isActive ? "text-signal" : "hover:text-signal-soft hover:bg-white/5"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
            <button
              onClick={() => setMobileMenuOpen(false)}
              className="absolute top-6 right-6 text-gray-400 hover:text-white"
              aria-label="Close menu"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </nav>
        )}

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
