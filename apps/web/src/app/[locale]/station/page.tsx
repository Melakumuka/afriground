"use client";

import { useEffect, useState } from "react";

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
            OPS-MODULE 02 · LIVE TELEMETRY
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                {risk.station_name}
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-lg">
                Real-time RF, antenna and environmental telemetry with risk analysis.
              </p>
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
                {isConnected ? "WS Feed · Live" : "Feed · Offline"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-12 space-y-6">
        {/* Risk Scores Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-px bg-graphite-600/60 border border-graphite-600/60">
          <ScoreCard title="Overall Risk Score" score={risk.overall_score} />
          <ScoreCard title="Availability" score={risk.availability_score} />
          <ScoreCard title="Reliability" score={risk.reliability_score} />
          <ScoreCard title="Weather Risk" score={risk.weather_risk} />
        </div>

        {/* Live Telemetry Dashboard */}
        {telemetry && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* RF & Signal */}
            <div className="console-panel rounded-sm">
              <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
                <span className="mono-label text-signal-soft">RF & DEMODULATOR</span>
                <span className="font-mono text-[10px] text-graphite-mute">
                  {new Date(telemetry.timestamp).toLocaleTimeString()} UTC
                </span>
              </div>
              <div className="px-6 sm:px-8 py-6 space-y-5">
                <TelemetryRow label="Frequency (MHz)" value={telemetry.rf.frequency_mhz} />
                <TelemetryRow label="Signal Strength (dBm)" value={telemetry.rf.signal_dbm} highlight={true} />
                <TelemetryRow label="Modulation" value={telemetry.rf.modulation} />
                <TelemetryRow label="SNR (dB)" value={telemetry.signal_quality.snr_db} />
                <TelemetryRow
                  label="Lock Status"
                  value={telemetry.rf.lock ? "LOCKED" : "SEARCHING"}
                  valueClass={telemetry.rf.lock ? "text-green-soft font-bold" : "text-signal-soft"}
                />
              </div>
            </div>

            {/* Antenna & Environment */}
            <div className="console-panel rounded-sm">
              <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
                <span className="mono-label text-signal-soft">ANTENNA & ENVIRONMENT</span>
              </div>
              <div className="px-6 sm:px-8 py-6 space-y-5">
                <TelemetryRow label="Azimuth (°)" value={telemetry.antenna.azimuth} />
                <TelemetryRow label="Elevation (°)" value={telemetry.antenna.elevation} />
                <TelemetryRow label="Wind Speed (km/h)" value={telemetry.weather.wind_kph} />
                <TelemetryRow label="Battery" value={`${telemetry.power.battery_pct}%`} />
                <TelemetryRow
                  label="Main Power"
                  value={telemetry.power.main ? "ONLINE" : "OFFLINE"}
                  valueClass={telemetry.power.main ? "text-green-soft" : "text-signal-soft"}
                />
              </div>
            </div>
          </div>
        )}

        {!telemetry && (
          <div className="console-panel rounded-sm px-6 sm:px-8 py-20 text-center">
            <span className="signal-indicator inline-block" />
            <p className="mono-label text-steel-2 mt-4">ACQUIRING TELEMETRY FEED...</p>
          </div>
        )}

        {/* Recommendation footnote */}
        <p className="mono-label text-graphite-mute">
          RECOMMENDATION · {risk.recommendation.toUpperCase()}
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