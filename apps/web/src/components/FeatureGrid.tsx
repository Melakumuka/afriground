"use client";

import Link from "next/link";
import { useT } from "@/lib/useT";

type FeatureItem = {
  id: string;
  icon: string;
  title: string;
  badge: string;
  description: string;
  href: string;
  ctaText: string;
  highlights: string[];
};

export default function FeatureGrid({ currentLocale }: { currentLocale: string }) {
  const { t } = useT("Features");
  const f = (n: number, key: string, zh: string, en: string) => t(`f${n}_${key}`, zh, en);
  const features: FeatureItem[] = [
    {
      id: "scheduling",
      icon: "🗓️",
      badge: f(1, "badge", "SGP4 轨道引擎", "SGP4 Orbit Engine"),
      title: t("f1_title", "自动化过境调度", "Automated Pass Scheduling"),
      description: t("f1_desc", "基于实时 NORAD TLE 传播与硬件可用性的即时过境预报与多天线预订引擎。", "Instant pass prediction and multi-antenna reservation engine based on real-time NORAD TLE propagation and hardware availability."),
      href: `/${currentLocale}/booking`,
      ctaText: t("f1_cta", "打开调度向导", "Open Scheduling Wizard"),
      highlights: [f(1, "h1", "分钟级预订", "Sub-minute reservation"), f(1, "h2", "冲突自动解决", "Conflict auto-resolution"), f(1, "h3", "透明的按次付费定价", "Transparent pay-per-pass pricing")]
    },
    {
      id: "telemetry",
      icon: "📡",
      badge: f(2, "badge", "亚秒级 TT&C 数据流", "Sub-Second TT&C Stream"),
      title: t("f2_title", "实时遥测与地面站健康状态", "Live Telemetry & Station Health"),
      description: t("f2_desc", "实时天线指向（方位角/仰角）、射频解调器锁定状态、信噪比指标与环境风险分析。", "Real-time antenna pointing (Azimuth/Elevation), RF demodulator lock state, signal SNR metrics, and environmental risk analysis."),
      href: `/${currentLocale}/station`,
      ctaText: t("f2_cta", "启动遥测控制台", "Launch Telemetry Dashboard"),
      highlights: [f(2, "h1", "WebSocket 遥测流", "WebSocket telemetry stream"), f(2, "h2", "天气风险评估", "Weather risk scoring"), f(2, "h3", "应急天线控制", "Emergency antenna control")]
    },
    {
      id: "catalog",
      icon: "🛰️",
      badge: f(3, "badge", "高通量下传", "High-Throughput Downlink"),
      title: t("f3_title", "对地观测数据目录", "Earth Observation Data Catalog"),
      description: t("f3_desc", "自动化采集管道：接收下传载荷数据、解码 CCSDS 帧，并将影像直接交付至云存储。", "Automated ingestion pipeline that receives downlinked payload data, decodes CCSDS frames, and delivers imagery directly to cloud storage."),
      href: `/${currentLocale}/data`,
      ctaText: t("f3_cta", "浏览数据下传", "Browse Data Downlinks"),
      highlights: [f(3, "h1", "多光谱影像预览", "Multispectral imagery preview"), f(3, "h2", "云存储自动同步", "Cloud storage auto-sync"), f(3, "h3", "元数据搜索与筛选", "Metadata search & filter")]
    },
    {
      id: "network",
      icon: "🌍",
      badge: f(4, "badge", "联邦式架构", "Federated Architecture"),
      title: t("f4_title", "泛非地面聚合", "Pan-African Ground Aggregation"),
      description: t("f4_desc", "通过一份统一的 GSaaS 合同，在 6 个非洲国家使用 14 面高增益抛物面天线，无需自建本地基础设施。", "Access 14 high-gain parabolic antennas across 6 African nations under a single unified GSaaS contract without managing local infrastructure."),
      href: `/${currentLocale}/station`,
      ctaText: t("f4_cta", "探索网络枢纽", "Explore Network Hubs"),
      highlights: [f(4, "h1", "S / X / Ka / UHF 频段", "S / X / Ka / UHF bands"), f(4, "h2", "3.7 米至 12.0 米天线口径", "3.7m to 12.0m dish aperture"), f(4, "h3", "冗余光纤回程", "Redundant fiber backhaul")]
    },
    {
      id: "api",
      icon: "⚡",
      badge: f(5, "badge", "REST 与 WebSockets", "REST & WebSockets"),
      title: t("f5_title", "开放 API 与云接入", "Open API & Cloud Ingestion"),
      description: t("f5_desc", "通过现代 REST 与 WebSocket API，将地面站调度和遥测数据流无缝集成到您的任务控制软件中。", "Seamlessly integrate ground station scheduling and telemetry feeds directly into your mission control software via modern REST & WebSocket APIs."),
      href: `/${currentLocale}/support`,
      ctaText: t("f5_cta", "查看开发者文档", "View Developer Docs"),
      highlights: [f(5, "h1", "Swagger / OpenAPI 规范", "Swagger / OpenAPI spec"), f(5, "h2", "Python 与 Node SDK", "SDK for Python & Node"), f(5, "h3", "OAuth2 与 API Key 认证", "OAuth2 & API Key auth")]
    },
    {
      id: "support",
      icon: "🛡️",
      badge: f(6, "badge", "99.98% SLA 可用率", "99.98% SLA Uptime"),
      title: t("f6_title", "24/7 太空运营支持", "24/7 Space Operations Support"),
      description: t("f6_desc", "专职卫星运营支持团队全天候监控天线健康、天气状况并处理应急联络。", "Dedicated satellite operations support team monitoring antenna health, weather conditions, and emergency contact passes around the clock."),
      href: `/${currentLocale}/support`,
      ctaText: t("f6_cta", "联系太空运营团队", "Contact Space Ops"),
      highlights: [f(6, "h1", "优先工单响应", "Priority ticket response"), f(6, "h2", "过境退款保障", "Pass refund guarantee"), f(6, "h3", "应急越权热线", "Emergency override hotline")]
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {features.map((item) => (
        <div
          key={item.id}
          className="glass-panel glass-panel-hover p-8 rounded-2xl flex flex-col justify-between border border-slate-800 relative group overflow-hidden"
        >
          {/* Subtle gradient hover accent */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/15 transition-all" />

          <div>
            {/* Top Icon & Badge */}
            <div className="flex justify-between items-start mb-6">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-slate-900 to-slate-800 border border-slate-700 flex items-center justify-center text-2xl shadow-lg group-hover:scale-110 transition-transform">
                {item.icon}
              </div>
              <span className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[11px] font-mono font-semibold rounded-full">
                {item.badge}
              </span>
            </div>

            <h3 className="text-xl font-bold text-white mb-3 group-hover:text-cyan-300 transition-colors">
              {item.title}
            </h3>

            <p className="text-slate-400 text-sm leading-relaxed mb-6">
              {item.description}
            </p>

            {/* Highlights List */}
            <ul className="space-y-2 mb-8 text-xs font-mono text-slate-300">
              {item.highlights.map((h, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className="text-cyan-400 font-bold">✓</span>
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Action Link */}
          <Link
            href={item.href}
            className="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/40 text-cyan-400 font-semibold text-xs font-mono tracking-wider flex items-center justify-between transition-all group-hover:shadow-lg"
          >
            <span>{item.ctaText}</span>
            <span className="group-hover:translate-x-1 transition-transform">→</span>
          </Link>
        </div>
      ))}
    </div>
  );
}
