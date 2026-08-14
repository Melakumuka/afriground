"use client";

import Link from "next/link";

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
  const features: FeatureItem[] = [
    {
      id: "scheduling",
      icon: "🗓️",
      badge: "SGP4 Orbit Engine",
      title: "Automated Pass Scheduling",
      description: "Instant pass prediction and multi-antenna reservation engine based on real-time NORAD TLE propagation and hardware availability.",
      href: `/${currentLocale}/booking`,
      ctaText: "Open Scheduling Wizard",
      highlights: ["Sub-minute reservation", "Conflict auto-resolution", "Transparent pay-per-pass pricing"]
    },
    {
      id: "telemetry",
      icon: "📡",
      badge: "Sub-Second TT&C Stream",
      title: "Live Telemetry & Station Health",
      description: "Real-time antenna pointing (Azimuth/Elevation), RF demodulator lock state, signal SNR metrics, and environmental risk analysis.",
      href: `/${currentLocale}/station`,
      ctaText: "Launch Telemetry Dashboard",
      highlights: ["WebSocket telemetry stream", "Weather risk scoring", "Emergency antenna control"]
    },
    {
      id: "catalog",
      icon: "🛰️",
      badge: "High-Throughput Downlink",
      title: "Earth Observation Data Catalog",
      description: "Automated ingestion pipeline that receives downlinked payload data, decodes CCSDS frames, and delivers imagery directly to cloud storage.",
      href: `/${currentLocale}/data`,
      ctaText: "Browse Data Downlinks",
      highlights: ["Multispectral imagery preview", "Cloud storage auto-sync", "Metadata search & filter"]
    },
    {
      id: "network",
      icon: "🌍",
      badge: "Federated Architecture",
      title: "Pan-African Ground Aggregation",
      description: "Access 14 high-gain parabolic antennas across 6 African nations under a single unified GSaaS contract without managing local infrastructure.",
      href: `/${currentLocale}/station`,
      ctaText: "Explore Network Hubs",
      highlights: ["S / X / Ka / UHF bands", "3.7m to 12.0m dish aperture", "Redundant fiber backhaul"]
    },
    {
      id: "api",
      icon: "⚡",
      badge: "REST & WebSockets",
      title: "Open API & Cloud Ingestion",
      description: "Seamlessly integrate ground station scheduling and telemetry feeds directly into your mission control software via modern REST & WebSocket APIs.",
      href: `/${currentLocale}/support`,
      ctaText: "View Developer Docs",
      highlights: ["Swagger / OpenAPI spec", "SDK for Python & Node", "OAuth2 & API Key auth"]
    },
    {
      id: "support",
      icon: "🛡️",
      badge: "99.98% SLA Uptime",
      title: "24/7 Space Operations Support",
      description: "Dedicated satellite operations support team monitoring antenna health, weather conditions, and emergency contact passes around the clock.",
      href: `/${currentLocale}/support`,
      ctaText: "Contact Space Ops",
      highlights: ["Priority ticket response", "Pass refund guarantee", "Emergency override hotline"]
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
