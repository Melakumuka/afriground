"use client";

import Link from "next/link";
import { useT } from "@/lib/useT";

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
  const { t, isZh, ns } = useT("Footer");
  const hubs: string[] = Array.isArray(ns.hubs_stations) ? (ns.hubs_stations as string[]) : isZh ? ["恩托托天文台", "哈特比斯霍克站", "马林迪站", "阿布贾枢纽", "开罗网关站", "达喀尔大西洋站"] : ["Entoto Observatory", "Hartebeesthoek", "Malindi Terminal", "Abuja Hub", "Cairo Gateway", "Dakar Atlantic"];

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
              {t("tagline", "非洲首屈一指的多地面站聚合平台，提供卫星过境调度、TT&C 与对地观测数据下传的 GSaaS 服务。", "Africa's premier multi-ground-station aggregator and Ground Station as a Service (GSaaS) platform for satellite pass scheduling, TT&C, and Earth observation downlinks.")}
            </p>

            <div className="flex items-center gap-3 pt-2">
              <span className="px-2.5 py-1 text-xs border border-graphite-600 text-steel-2 font-mono">
                {t("ccsds", "符合 CCSDS 标准", "CCSDS Compliant")}
              </span>
              <span className="px-2.5 py-1 text-xs border border-graphite-600 text-steel-2 font-mono">
                {t("itu", "ITU 频段许可", "ITU Band Cleared")}
              </span>
              <span className="px-2.5 py-1 text-xs border border-green/40 text-green-soft font-mono">
                {t("iso", "ISO 27001", "ISO 27001")}
              </span>
            </div>
          </div>

          {/* Col 2: Platform Modules */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              {t("modules_title", "GSaaS 模块", "GSaaS Modules")}
            </h4>
            <ul className="space-y-2.5 text-graphite-mute">
              <li>
                <Link href={`/${currentLocale}/booking`} className="hover:text-signal-soft transition-colors">
                  {t("module_scheduling", "过境调度与报价", "Pass Scheduling & Quote")}
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/station`} className="hover:text-signal-soft transition-colors">
                  {t("module_telemetry", "实时遥测与风险评估", "Live Telemetry & Risk")}
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/data`} className="hover:text-signal-soft transition-colors">
                  {t("module_catalog", "数据下传", "Data Catalog")}
                </Link>
              </li>
              <li>
                <Link href={`/${currentLocale}/support`} className="hover:text-signal-soft transition-colors">
                  {t("module_support", "SLA & 支持", "SLA & Support")}
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Key Ground Stations */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              {t("hubs_title", "地面站网络枢纽", "Station Network Hubs")}
            </h4>
            <ul className="space-y-2.5 text-graphite-mute font-mono text-xs">
              {hubs.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
          </div>

          {/* Col 4: Operations & Contact */}
          <div>
            <h4 className="text-white font-bold text-sm tracking-wider uppercase font-mono mb-4">
              {t("ops_title", "太空运营台", "Space Ops Desk")}
            </h4>
            <div className="space-y-3 text-graphite-mute text-xs font-mono">
              <p>{t("ops_address", "埃塞俄比亚亚的斯亚贝巴恩托托航天研究所", "Entoto Space Institute, Addis Ababa, Ethiopia")}</p>
              <p>{t("ops_email", "ops@afriground.space", "ops@afriground.space")}</p>
              <p>{t("ops_hotline", "24/7 热线：+251 (0) 11 896 1234", "24/7 Hotline: +251 (0) 11 896 1234")}</p>
              <div className="pt-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 border border-green/40 text-green-soft text-[11px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-soft animate-ping" />
                  {t("feeds_live", "遥测数据流在线", "Telemetry Feeds Live")}
                </span>
              </div>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-graphite-600/50 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-graphite-mute font-mono">
          <p>{t("rights", "© {year} AfriGround GSaaS 平台。保留所有权利。", "© {year} AfriGround GSaaS Platform. All rights reserved.").replace("{year}", String(new Date().getFullYear()))}</p>
          <div className="flex gap-6">
            <span className="hover:text-steel-2 cursor-pointer">{t("privacy", "隐私政策", "Privacy Policy")}</span>
            <span className="hover:text-steel-2 cursor-pointer">{t("terms", "服务条款", "Terms of Service")}</span>
            <span className="hover:text-steel-2 cursor-pointer">{t("api_ref", "API 参考", "API Reference")}</span>
          </div>
        </div>

      </div>
    </footer>
  );
}