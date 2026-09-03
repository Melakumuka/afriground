"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useMessages } from "next-intl";
import { useEffect, useState, useRef } from "react";

interface NavItem {
  href: string;
  label: string;
  desc?: string;
  badge?: string;
  icon?: string;
}

interface NavCategory {
  category: string;
  categoryZh: string;
  items: NavItem[];
}

export default function Navbar({ currentLocale }: { currentLocale: string }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [moreDropdownOpen, setMoreDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Access raw messages object safely
  const messages = useMessages() as Record<string, Record<string, string>>;
  const nav = messages?.Navigation || {};
  const isZh = currentLocale === "zh";

  // Navigation structured by domains
  const navCategories: NavCategory[] = [
    {
      category: "OPERATIONS & CONTROL",
      categoryZh: "运营与控制",
      items: [
        {
          href: `/${currentLocale}`,
          label: nav.dashboard || (isZh ? "控制台" : "Dashboard"),
          desc: isZh ? "实时轨道视窗与网络全景" : "Live orbital viewport & network overview",
          icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
        },
        {
          href: `/${currentLocale}/station`,
          label: nav.network || (isZh ? "地面站网络" : "Ground Station Network"),
          desc: isZh ? "地面站数字孪生与遥测状态" : "Station digital twin & telemetry feeds",
          badge: "TWIN",
          icon: "M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0",
        },
        {
          href: `/${currentLocale}/operations`,
          label: nav.operations || (isZh ? "任务运营与过境" : "Active Operations"),
          desc: isZh ? "过境执行、就绪事件与任务队列" : "Pass execution, readiness & job logs",
          icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
        },
        {
          href: `/${currentLocale}/booking`,
          label: nav.scheduling || (isZh ? "过境调度与预订" : "Pass Scheduling"),
          desc: isZh ? "LEO/MEO 窗口冲突矩阵与即时预订" : "LEO/MEO orbital window booking matrix",
          badge: "HOT",
          icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z",
        },
      ],
    },
    {
      category: "FLEET & ASSETS",
      categoryZh: "星座与资产注册",
      items: [
        {
          href: `/${currentLocale}/missions`,
          label: nav.satellites || (isZh ? "卫星星座管理" : "Satellites & Fleet"),
          desc: isZh ? "已注册卫星轨道参数与 ICD 状态" : "Registered spacecraft TLEs & ICDs",
          icon: "M13 10V3L4 14h7v7l9-11h-7z",
        },
        {
          href: `/${currentLocale}/missions/new`,
          label: nav.missions_new || (isZh ? "注册新卫星 (ICD)" : "Register Satellite"),
          desc: isZh ? "配置射频下传参数与频段授权" : "Onboard spacecraft RF profile & transponders",
          icon: "M12 4v16m8-8H4",
        },
        {
          href: `/${currentLocale}/station/new`,
          label: nav.station_new || (isZh ? "接入新地面站" : "Register Station"),
          desc: isZh ? "将天线终端接入 AfriGround 网关" : "Federate dish terminal & edge gateway",
          icon: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10",
        },
      ],
    },
    {
      category: "DATA & COMMERCIAL",
      categoryZh: "数据与商务",
      items: [
        {
          href: `/${currentLocale}/data`,
          label: nav.catalog || (isZh ? "数据下传目录" : "Data Downlinks"),
          desc: isZh ? "CCSDS 解码数据集与下传记录" : "Demodulated raw frames & telemetry files",
          icon: "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4",
        },
        {
          href: `/${currentLocale}/data/egress`,
          label: nav.egress || (isZh ? "云端出口配置" : "Cloud Egress"),
          desc: isZh ? "直连 AWS S3, Azure Blob 或 GCS 存储桶" : "Direct push to AWS S3, Azure Blob, GCS",
          icon: "M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12",
        },
        {
          href: `/${currentLocale}/commercial`,
          label: nav.commercial || (isZh ? "商务合同与 SLA" : "Commercial & SLA"),
          desc: isZh ? "预留容量合同、SLA 违约监测与账单" : "Reserved capacity, SLA tracking & billing",
          icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
        },
        {
          href: `/${currentLocale}/commercial/quotes`,
          label: nav.quotes || (isZh ? "商务报价计算器" : "Quote Calculator"),
          desc: isZh ? "按分预订与按月预留容量估价" : "Estimate on-demand & reserved pass pricing",
          icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
        },
      ],
    },
    {
      category: "SUPPORT & ASSISTANCE",
      categoryZh: "支持与服务",
      items: [
        {
          href: `/${currentLocale}/support`,
          label: nav.support || (isZh ? "技术支持工单" : "SLA & Support"),
          desc: isZh ? "24/7 空间运营台与工单提交" : "24/7 Space ops desk & incident tracking",
          icon: "M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z",
        },
        {
          href: `/${currentLocale}/contact`,
          label: nav.contact || (isZh ? "联系 AfriGround" : "Contact Team"),
          desc: isZh ? "业务咨询、专用地面站建设与网络接入" : "Commercial inquiries & custom station setups",
          icon: "M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
        },
      ],
    },
  ];

  // Primary links for Desktop Navbar
  const primaryDesktopLinks = [
    {
      href: `/${currentLocale}/network`,
      label: nav.network || (isZh ? "地面站网络" : "Ground Station Network"),
    },
    {
      href: `/${currentLocale}/booking`,
      label: nav.scheduling || (isZh ? "过境调度" : "Scheduling"),
    },
    {
      href: `/${currentLocale}/missions`,
      label: nav.satellites || (isZh ? "卫星管理" : "Satellites"),
    },
    {
      href: `/${currentLocale}/data`,
      label: nav.catalog || (isZh ? "数据下传" : "Data"),
    },
  ];

  // Switch locale handler
  const toggleLocale = () => {
    const nextLocale = isZh ? "en" : "zh";
    const newPath = pathname.replace(`/${currentLocale}`, `/${nextLocale}`);
    router.push(newPath || `/${nextLocale}`);
  };

  // Close mobile menu on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setMobileMenuOpen(false);
        setMoreDropdownOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Prevent background scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileMenuOpen]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setMoreDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <>
    <header className="sticky top-0 z-50 w-full bg-graphite/90 backdrop-blur-xl border-b border-graphite-600/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo */}
        <Link
          href={`/${currentLocale}`}
          className="flex items-center gap-3 group z-50"
        >
          <div className="w-10 h-10 bg-signal flex items-center justify-center group-hover:scale-105 transition-transform">
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M2.5 19.5a12 12 0 0 1 19 0"
                stroke="#15171A"
                strokeWidth="1.6"
                strokeLinecap="round"
              />
              <path
                d="M12 19.5V7M12 7l-3.4 3.6M12 7l3.4 3.6M12 4v3"
                stroke="#15171A"
                strokeWidth="1.6"
                strokeLinecap="round"
              />
              <circle cx="12" cy="19.5" r="1.3" fill="#15171A" />
            </svg>
          </div>
          <div>
            <span className="text-xl font-black tracking-tight text-white font-display">
              Afri<span className="text-signal-soft">Ground</span>
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links (Visible on xl+) */}
        <nav className="hidden xl:flex items-center gap-1">
          {primaryDesktopLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 text-sm font-medium transition-all rounded-md ${
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

        {/* Desktop Network Status & Actions (Visible on xl+) */}
        <div className="hidden xl:flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 border border-graphite-600 text-xs text-steel-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-soft opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-soft"></span>
            </span>
            <span className="font-mono text-green-soft font-semibold">
              {nav.nodes_online ||
                (isZh ? "14/14 网络节点在线" : "14/14 Network Nodes Online")}
            </span>
          </div>

          <button
            onClick={toggleLocale}
            className="px-3 py-1.5 border border-graphite-600 text-steel-2 hover:text-white hover:border-graphite-500 text-xs font-mono tracking-wider transition-all cursor-pointer rounded-md"
            title={isZh ? "切换语言" : "Switch Language"}
          >
            {currentLocale.toUpperCase()}
          </button>

        </div>

        {/* Mobile Hamburger Button (Visible below xl) */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="xl:hidden p-2 text-steel-2 hover:text-white z-50 focus:outline-none"
          aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
        >
          {mobileMenuOpen ? (
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          ) : (
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 12h18M3 6h18M3 18h18" />
            </svg>
          )}
        </button>
      </div>
    </header>



      {/* Mobile & Tablet Full Screen Overlay Menu */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-x-0 top-20 bottom-0 z-50 bg-graphite/98 backdrop-blur-2xl overflow-y-auto lg:hidden flex flex-col border-t border-graphite-600/80 animate-fade-up"
          role="dialog"
          aria-modal="true"
        >
          <div className="flex-1 max-w-xl mx-auto w-full px-4 sm:px-6 py-6 pb-28 space-y-7">
            
            {/* Live Network Status Banner */}
            <div className="flex items-center justify-between p-3.5 bg-graphite-800 border border-graphite-600/80 rounded-lg">
              <div className="flex items-center gap-2.5">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-soft opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-soft"></span>
                </span>
                <span className="font-mono text-green-soft text-xs font-semibold">
                  {nav.nodes_online || (isZh ? "14/14 网络节点在线" : "14/14 Network Nodes Online")}
                </span>
              </div>
              <span className="text-[11px] font-mono text-steel uppercase bg-graphite-700 px-2 py-0.5 rounded">
                LEO/MEO/GEO
              </span>
            </div>

            {/* Categorized Navigation Link Groups */}
            {navCategories.map((group, groupIdx) => (
              <div key={groupIdx} className="space-y-2.5">
                {/* Category Header */}
                <div className="flex items-center justify-between border-b border-graphite-600/60 pb-1.5">
                  <span className="font-mono text-xs font-bold text-steel tracking-wider uppercase">
                    {isZh ? group.categoryZh : group.category}
                  </span>
                  <span className="text-[10px] font-mono text-graphite-mute">
                    0{groupIdx + 1}
                  </span>
                </div>

                {/* Group Items */}
                <div className="grid grid-cols-1 gap-2 pt-1">
                  {group.items.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                      <Link
                        key={link.href}
                        href={link.href}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`group flex items-start gap-3.5 p-3 rounded-lg border transition-all ${
                          isActive
                            ? "bg-signal/15 border-signal/50 text-white shadow-lg shadow-signal/10"
                            : "bg-graphite-800/60 border-graphite-600/40 text-steel-2 hover:bg-graphite-700/80 hover:text-white hover:border-graphite-500"
                        }`}
                      >
                        {/* Icon */}
                        {link.icon && (
                          <div
                            className={`p-2 rounded-md transition-colors shrink-0 mt-0.5 ${
                              isActive
                                ? "bg-signal text-graphite"
                                : "bg-graphite-700 text-steel-2 group-hover:text-white group-hover:bg-graphite-600"
                            }`}
                          >
                            <svg
                              width="18"
                              height="18"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            >
                              <path d={link.icon} />
                            </svg>
                          </div>
                        )}

                        {/* Title & Description */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span
                              className={`text-base font-semibold leading-tight ${
                                isActive ? "text-signal-soft font-bold" : "text-white"
                              }`}
                            >
                              {link.label}
                            </span>
                            {link.badge && (
                              <span
                                className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                                  link.badge === "HOT"
                                    ? "bg-signal text-graphite"
                                    : "bg-graphite-600 text-green-soft border border-green/30"
                                }`}
                              >
                                {link.badge}
                              </span>
                            )}
                          </div>
                          {link.desc && (
                            <p className="text-xs text-graphite-mute mt-1 line-clamp-1">
                              {link.desc}
                            </p>
                          )}
                        </div>

                        {/* Chevron */}
                        <svg
                          width="16"
                          height="16"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className={`shrink-0 mt-2.5 transition-transform ${
                            isActive
                              ? "text-signal translate-x-0.5"
                              : "text-graphite-mute group-hover:text-white group-hover:translate-x-0.5"
                          }`}
                        >
                          <path d="M9 18l6-6-6-6" />
                        </svg>
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}

            {/* Mobile Footer Actions */}
            <div className="pt-4 border-t border-graphite-600/80 space-y-3">
              <Link
                href={`/${currentLocale}/booking`}
                onClick={() => setMobileMenuOpen(false)}
                className="w-full py-3.5 bg-signal hover:bg-signal-soft text-graphite font-bold text-center text-sm uppercase tracking-wider rounded-lg shadow-xl shadow-signal/20 flex items-center justify-center gap-2 transition-transform active:scale-98"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{nav.schedule_pass || (isZh ? "预订过境服务" : "Schedule a Pass")}</span>
              </Link>

              <button
                type="button"
                onClick={() => {
                  toggleLocale();
                  setMobileMenuOpen(false);
                }}
                className="w-full py-3 border border-graphite-600 text-steel-2 hover:text-white hover:bg-graphite-700 font-mono text-xs tracking-wider transition-all rounded-lg flex items-center justify-center gap-2 cursor-pointer"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
                </svg>
                <span>{isZh ? "Switch to English (EN)" : "切换为简体中文 (ZH)"}</span>
              </button>
            </div>

          </div>
        </div>
      )}
    </>
  );
}

