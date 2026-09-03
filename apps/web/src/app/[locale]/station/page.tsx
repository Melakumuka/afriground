"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useT } from "@/lib/useT";
import type { Agent, Station, TimeStatus } from "@/lib/api";

// Types matching our backend
type StationRisk = {
  station_name: string;
  overall_score: number;
  availability_score: number;
  reliability_score: number;
  weather_risk: number;
  recommendation: string;
};

type TelemetryData = {
  timestamp: string;
  antenna: { azimuth: number; elevation: number };
  rf: { frequency_mhz: number; signal_dbm: number; lock: boolean; modulation: string };
  signal_quality: { snr_db: number; ber: number; eb_n0: number };
  weather: { temp_c: number; wind_kph: number; rain: boolean };
  power: { main: boolean; ups: boolean; battery_pct: number };
};

export default function StationHealthDashboard() {
  const params = useParams();
  const { t } = useT("Station");
  const [station, setStation] = useState<Station | null>(null);
  const [agents, setAgents] = useState<Agent[] | null>(null);
  const [timeStatus, setTimeStatus] = useState<TimeStatus[] | null>(null);
  const [stationName, setStationName] = useState("Entoto Observatory · Antenna A (12m)");

  // Mock data for MVP UI
  const [risk] = useState<StationRisk>({
    station_name: "Entoto Observatory · Antenna A (12m)",
    overall_score: 92.5,
    availability_score: 100,
    reliability_score: 98,
    weather_risk: 85,
    recommendation: "Preferred — high confidence for scheduling",
  });

  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Phase 4.2 — resolve the station twin from the API (falls back to the
  // simulated feed when the backend is unreachable).
  useEffect(() => {
    fetch("/api/platform/stations")
      .then((res) => (res.ok ? res.json() : null))
      .then(async (payload) => {
        if (!payload?.ok || !Array.isArray(payload.data) || payload.data.length === 0) return;
        const first: Station = payload.data[0];
        setStation(first);
        setStationName(`${first.name} · ${first.code}`);
        const [agentsRes, timeRes] = await Promise.all([
          fetch(`/api/platform/stations/${first.id}/agents`).then((r) => (r.ok ? r.json() : null)),
          fetch(`/api/platform/stations/${first.id}/time-status`).then((r) => (r.ok ? r.json() : null)),
        ]);
        if (agentsRes?.ok) setAgents(agentsRes.data);
        if (timeRes?.ok) setTimeStatus(timeRes.data);
      })
      .catch(() => {
        /* API unreachable — keep simulated feed */
      });
  }, []);

  // Connect to telemetry websocket
  useEffect(() => {
    // In a real app, this would point to the backend WS URL
    // For MVP UI display, we'll simulate the WebSocket feed locally
    const connect = setTimeout(() => setIsConnected(true), 0);

    const interval = setInterval(() => {
      setTelemetry({
        timestamp: new Date().toISOString(),
        antenna: {
          azimuth: +(Math.random() * 360).toFixed(1),
          elevation: +(45 + Math.random() * 10).toFixed(1),
        },
        rf: {
          frequency_mhz: 2200.0,
          signal_dbm: +(-65 + Math.random() * 5).toFixed(1),
          lock: true,
          modulation: "QPSK",
        },
        signal_quality: {
          snr_db: +(15 + Math.random() * 2).toFixed(1),
          ber: 0.000001,
          eb_n0: 12.5,
        },
        weather: {
          temp_c: 22.5,
          wind_kph: +(10 + Math.random() * 5).toFixed(1),
          rain: false,
        },
        power: { main: true, ups: false, battery_pct: 100 },
      });
    }, 1000);

    return () => {
      clearInterval(interval);
      clearTimeout(connect);
      setIsConnected(false);
    };
  }, []);

  return (
    <main className="min-h-screen bg-graphite text-ink">
      {/* ── Ops header ─────────────────────────────────────────── */}
      <div className="border-b border-graphite-600/60">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-14">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("module", "运营模块 02 · 实时遥测", "OPS-MODULE 02 · LIVE TELEMETRY")}
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                {stationName}
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-lg">
                {station ? `${station.country} · ${station.certification_state} · TX ${station.tx_enabled ? "ENABLED" : "DISABLED"} · ` : ""}
                {t("subtitle", "实时射频、天线与环境遥测数据，并附带风险分析。", "Real-time RF, antenna and environmental telemetry with risk analysis.")}
              </p>
              <div className="mt-6">
                <Link 
                  href={`/${params.locale}/operations/jobs/00000000-0000-0000-0000-000000000000`}
                  className="inline-flex items-center gap-2 px-4 py-2 border border-signal text-signal hover:bg-signal hover:text-black transition-colors"
                >
                  {t("pass_report", "查看样本任务报告", "View Sample Pass Report")}
                </Link>
              </div>
            </div>
            <div
              className={`flex items-center gap-2 px-3 py-1.5 border ${
                isConnected ? "border-green/50" : "border-signal/60"
              }`}
            >
              <span className="relative flex h-2 w-2">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    isConnected ? "bg-green-soft" : "bg-signal"
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2 w-2 ${
                    isConnected ? "bg-green-soft" : "bg-signal"
                  }`}
                />
              </span>
              <span className={`mono-label ${isConnected ? "text-green-soft" : "text-signal-soft"}`}>
                {isConnected ? t("feed_live", "WS 数据流 · 实时", "WS Feed · Live") : t("feed_offline", "数据流 · 离线", "Feed · Offline")}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-12 space-y-6">
        {/* Risk Scores Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-px bg-graphite-600/60 border border-graphite-600/60">
          <ScoreCard title={t("overall", "综合风险评分", "Overall Risk Score")} score={risk.overall_score} />
          <ScoreCard title={t("availability", "可用性", "Availability")} score={risk.availability_score} />
          <ScoreCard title={t("reliability", "可靠性", "Reliability")} score={risk.reliability_score} />
          <ScoreCard title={t("weather", "天气风险", "Weather Risk")} score={risk.weather_risk} />
        </div>

        {/* Live Telemetry Dashboard */}
        {telemetry && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* RF & Signal */}
            <div className="console-panel rounded-sm">
              <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
                <span className="mono-label text-signal-soft">{t("rf_panel", "射频与解调器", "RF & DEMODULATOR")}</span>
                <span className="font-mono text-[10px] text-graphite-mute">
                  {new Date(telemetry.timestamp).toLocaleTimeString([], { timeZone: "UTC" })} UTC
                </span>
              </div>
              <div className="px-6 sm:px-8 py-6 space-y-5">
                <TelemetryRow label={t("frequency", "频率（MHz）", "Frequency (MHz)")} value={telemetry.rf.frequency_mhz} />
                <TelemetryRow label={t("signal", "信号强度（dBm）", "Signal Strength (dBm)")} value={telemetry.rf.signal_dbm} highlight={true} />
                <TelemetryRow label={t("modulation", "调制方式", "Modulation")} value={telemetry.rf.modulation} />
                <TelemetryRow label={t("snr", "信噪比（dB）", "SNR (dB)")} value={telemetry.signal_quality.snr_db} />
                <TelemetryRow
                  label={t("lock", "锁定状态", "Lock Status")}
                  value={telemetry.rf.lock ? t("locked", "已锁定", "LOCKED") : t("searching", "搜索中", "SEARCHING")}
                  valueClass={telemetry.rf.lock ? "text-green-soft font-bold" : "text-signal-soft"}
                />
              </div>
            </div>

            {/* Antenna & Environment */}
            <div className="console-panel rounded-sm">
              <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
                <span className="mono-label text-signal-soft">{t("ant_panel", "天线与环境", "ANTENNA & ENVIRONMENT")}</span>
              </div>
              <div className="px-6 sm:px-8 py-6 space-y-5">
                <TelemetryRow label={t("azimuth", "方位角（°）", "Azimuth (°)")} value={telemetry.antenna.azimuth} />
                <TelemetryRow label={t("elevation", "仰角（°）", "Elevation (°)")} value={telemetry.antenna.elevation} />
                <TelemetryRow label={t("wind", "风速（km/h）", "Wind Speed (km/h)")} value={telemetry.weather.wind_kph} />
                <TelemetryRow label={t("battery", "电池", "Battery")} value={`${telemetry.power.battery_pct}%`} />
                <TelemetryRow
                  label={t("main_power", "主电源", "Main Power")}
                  value={telemetry.power.main ? t("online", "在线", "ONLINE") : t("offline", "离线", "OFFLINE")}
                  valueClass={telemetry.power.main ? "text-green-soft" : "text-signal-soft"}
                />
              </div>
            </div>
          </div>
        )}

        {!telemetry && (
          <div className="console-panel rounded-sm px-6 sm:px-8 py-20 text-center">
            <span className="signal-indicator inline-block" />
            <p className="mono-label text-steel-2 mt-4">{t("acquiring", "正在获取遥测数据流...", "ACQUIRING TELEMETRY FEED...")}</p>
          </div>
        )}

        {(agents || timeStatus) && (
          <div className="console-panel rounded-sm">
            <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
              <span className="mono-label text-signal-soft">{t("platform_panel", "平台 · 边缘代理与时钟同步", "PLATFORM · EDGE AGENTS & CLOCK SYNC")}</span>
              <span className="font-mono text-[10px] text-green-soft">LIVE · API FEED</span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-px bg-graphite-600/60">
              <div className="px-6 sm:px-8 py-6 space-y-4">
                <span className="mono-label text-steel-2">{t("agents_label", "已注册边缘代理", "REGISTERED EDGE AGENTS")}</span>
                {(agents ?? []).length === 0 && (
                  <p className="font-mono text-xs text-graphite-mute">—</p>
                )}
                {(agents ?? []).map((a) => (
                  <div key={a.id} className="flex items-center justify-between py-2 border-b border-graphite-600/40 last:border-0">
                    <div>
                      <div className="font-mono text-sm text-white">{a.agent_id}</div>
                      <div className="font-mono text-[10px] text-graphite-mute">
                        v{a.agent_version ?? "?"} · {a.last_heartbeat_at ? new Date(a.last_heartbeat_at).toLocaleTimeString([], { timeZone: "UTC" }) : "no heartbeat"}
                      </div>
                    </div>
                    <span
                      className={`px-2 py-0.5 text-[10px] font-mono border ${
                        a.status === "active" && !a.revoked_at
                          ? "text-green-soft border-green/40"
                          : "text-signal-soft border-signal/40"
                      }`}
                    >
                      {a.status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
              <div className="px-6 sm:px-8 py-6 space-y-4">
                <span className="mono-label text-steel-2">{t("sync_label", "时间同步状态", "TIME SYNC STATUS")}</span>
                {(timeStatus ?? []).length === 0 && (
                  <p className="font-mono text-xs text-graphite-mute">—</p>
                )}
                {(timeStatus ?? []).slice(0, 6).map((s) => (
                  <div key={s.id} className="flex items-center justify-between py-2 border-b border-graphite-600/40 last:border-0">
                    <div>
                      <div className="font-mono text-sm text-white">{s.sync_status}</div>
                      <div className="font-mono text-[10px] text-graphite-mute">{s.clock_source ?? "—"}</div>
                    </div>
                    <span className="font-mono text-xs text-signal-soft">
                      {s.offset_ms != null ? `${s.offset_ms >= 0 ? "+" : ""}${s.offset_ms} ms` : "—"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Recommendation footnote */}
        <p className="mono-label text-graphite-mute">
          {t("recommendation", "建议 · ", "RECOMMENDATION · ")}{t("rec_preferred", "首选——调度置信度高", "Preferred — high confidence for scheduling").toUpperCase()}
        </p>
      </div>
    </main>
  );
}

// ── UI Components ──────────────────────────────────────────────────────────

function ScoreCard({ title, score }: { title: string; score: number }) {
  const color = score >= 90 ? "text-green-soft" : score >= 70 ? "text-signal-soft" : "text-signal";
  const border = score >= 90 ? "border-green/40" : score >= 70 ? "border-signal/40" : "border-signal/60";

  return (
    <div className={`bg-graphite-800 p-6 flex flex-col justify-between border-l first:border-l-0 ${border} border-t md:border-t-0`}>
      <span className="mono-label text-steel-2">{title}</span>
      <div className={`font-display font-bold text-4xl mt-3 font-mono ${color}`}>
        {score.toFixed(1)}
      </div>
    </div>
  );
}

function TelemetryRow({
  label,
  value,
  highlight,
  valueClass,
}: {
  label: string;
  value: string | number;
  highlight?: boolean;
  valueClass?: string;
}) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-graphite-600/40 last:border-0">
      <span className="text-steel-2 font-medium">{label}</span>
      <span className={`font-mono text-lg ${highlight ? "text-signal-soft font-bold" : "text-white"} ${valueClass || ""}`}>
        {value}
      </span>
    </div>
  );
}