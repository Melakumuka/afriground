"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

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
  const t = useTranslations("Dashboard"); // Just reusing strings for MVP

  // Mock data for MVP UI
  const [risk, setRisk] = useState<StationRisk>({
    station_name: "Entoto Antenna A (12m)",
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
    setIsConnected(true);
    
    const interval = setInterval(() => {
      setTelemetry({
        timestamp: new Date().toISOString(),
        antenna: { 
          azimuth: +(Math.random() * 360).toFixed(1), 
          elevation: +(45 + Math.random() * 10).toFixed(1) 
        },
        rf: { 
          frequency_mhz: 2200.0, 
          signal_dbm: +(-65 + Math.random() * 5).toFixed(1), 
          lock: true, 
          modulation: "QPSK" 
        },
        signal_quality: { 
          snr_db: +(15 + Math.random() * 2).toFixed(1), 
          ber: 0.000001, 
          eb_n0: 12.5 
        },
        weather: { 
          temp_c: 22.5, 
          wind_kph: +(10 + Math.random() * 5).toFixed(1), 
          rain: false 
        },
        power: { main: true, ups: false, battery_pct: 100 }
      });
    }, 1000);

    return () => {
      clearInterval(interval);
      setIsConnected(false);
    };
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{risk.station_name}</h1>
            <p className="text-gray-500">Live Station Telemetry & Risk Analysis</p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`h-3 w-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-sm font-medium text-gray-600">
              {isConnected ? "Live Stream Active" : "Disconnected"}
            </span>
          </div>
        </div>

        {/* Risk Scores Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <ScoreCard title="Overall Risk Score" score={risk.overall_score} />
          <ScoreCard title="Availability" score={risk.availability_score} />
          <ScoreCard title="Reliability" score={risk.reliability_score} />
          <ScoreCard title="Weather Risk" score={risk.weather_risk} />
        </div>

        {/* Live Telemetry Dashboard */}
        {telemetry && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* RF & Signal */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">RF & Demodulator</h3>
              <div className="space-y-4">
                <TelemetryRow label="Frequency (MHz)" value={telemetry.rf.frequency_mhz} />
                <TelemetryRow label="Signal Strength (dBm)" value={telemetry.rf.signal_dbm} highlight={true} />
                <TelemetryRow label="Modulation" value={telemetry.rf.modulation} />
                <TelemetryRow label="SNR (dB)" value={telemetry.signal_quality.snr_db} />
                <TelemetryRow label="Lock Status" value={telemetry.rf.lock ? "LOCKED" : "SEARCHING"} 
                  valueClass={telemetry.rf.lock ? "text-green-600 font-bold" : "text-yellow-600"} />
              </div>
            </div>

            {/* Antenna & Environment */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Antenna & Environment</h3>
              <div className="space-y-4">
                <TelemetryRow label="Azimuth (°)" value={telemetry.antenna.azimuth} />
                <TelemetryRow label="Elevation (°)" value={telemetry.antenna.elevation} />
                <TelemetryRow label="Wind Speed (km/h)" value={telemetry.weather.wind_kph} />
                <TelemetryRow label="Main Power" value={telemetry.power.main ? "ONLINE" : "OFFLINE"} 
                  valueClass={telemetry.power.main ? "text-green-600" : "text-red-600"}/>
              </div>
            </div>

          </div>
        )}

      </div>
    </main>
  );
}

// ── UI Components ──────────────────────────────────────────────────────────

function ScoreCard({ title, score }: { title: string, score: number }) {
  // Determine color based on score (higher is better)
  const color = score >= 90 ? "text-green-600" : score >= 70 ? "text-yellow-600" : "text-red-600";
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
      <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">{title}</h4>
      <div className={`text-4xl font-bold mt-2 ${color}`}>
        {score.toFixed(1)}
      </div>
    </div>
  );
}

function TelemetryRow({ label, value, highlight, valueClass }: { label: string, value: string | number, highlight?: boolean, valueClass?: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-gray-50 last:border-0">
      <span className="text-gray-600 font-medium">{label}</span>
      <span className={`font-mono text-lg ${highlight ? 'text-blue-600 font-bold' : 'text-gray-900'} ${valueClass || ''}`}>
        {value}
      </span>
    </div>
  );
}
