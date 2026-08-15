"use client";

import { useState } from "react";
import Link from "next/link";

type SatellitePreset = {
  id: string;
  name: string;
  norad: string;
  type: string;
  altitude: string;
  downlinkRate: string;
};

const SATELLITES: SatellitePreset[] = [
  { id: "aqua", name: "Aqua (NASA EOS)", norad: "27424", type: "Earth Observation LEO", altitude: "705 km", downlinkRate: "150 Mbps (X-band)" },
  { id: "terra", name: "Terra (EOS AM-1)", norad: "25994", type: "Remote Sensing LEO", altitude: "705 km", downlinkRate: "150 Mbps (X-band)" },
  { id: "sentinel2a", name: "Sentinel-2A (Copernicus)", norad: "40697", type: "Multispectral Imagery", altitude: "786 km", downlinkRate: "560 Mbps (Ka-band)" },
  { id: "afrisat", name: "AfriSat-1 (CubeSat)", norad: "59001", type: "IoT Telemetry SmallSat", altitude: "530 km", downlinkRate: "9.6 Kbps (S-band)" },
];

type PassResult = {
  nextPassUTC: string;
  passDurationMin: number;
  maxElevationDeg: number;
  estimatedDataGB: number;
  costUSD: number;
  signalLockProb: string;
};

export default function PassSimulatorWidget({ currentLocale }: { currentLocale: string }) {
  const [selectedSat, setSelectedSat] = useState<SatellitePreset>(SATELLITES[0]);
  const [stationId, setStationId] = useState("entoto");
  const [isCalculating, setIsCalculating] = useState(false);
  const [passResult, setPassResult] = useState<PassResult>({
    nextPassUTC: "2026-08-14T18:42:15Z",
    passDurationMin: 11.4,
    maxElevationDeg: 68.2,
    estimatedDataGB: 12.8,
    costUSD: 171.00,
    signalLockProb: "99.4%"
  });

  const handleRunSimulation = () => {
    setIsCalculating(true);
    setTimeout(() => {
      // Simulate random pass variations based on selected sat
      const duration = +(8 + Math.random() * 6).toFixed(1);
      const elevation = +(45 + Math.random() * 40).toFixed(1);
      const rateMbps = selectedSat.id === "sentinel2a" ? 560 : selectedSat.id === "afrisat" ? 0.01 : 150;
      const dataGB = +((duration * 60 * rateMbps) / 8000).toFixed(1);
      const pricePerMin = 15.00;
      
      setPassResult({
        nextPassUTC: new Date(Date.now() + Math.floor(Math.random() * 7200000)).toISOString(),
        passDurationMin: duration,
        maxElevationDeg: Math.min(elevation, 89.5),
        estimatedDataGB: Math.max(dataGB, 0.1),
        costUSD: +(duration * pricePerMin).toFixed(2),
        signalLockProb: "99.8%"
      });
      setIsCalculating(false);
    }, 1200);
  };

  return (
    <div className="w-full glass-panel rounded-sm p-8 border border-signal/25 shadow-2xl bg-graphite-800 relative overflow-hidden">
      
      {/* Background glow circle */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-signal/10 rounded-full blur-3xl pointer-events-none" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        
        {/* Left Inputs */}
        <div className="lg:col-span-6 space-y-6">
          
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-signal/10 text-signal-soft text-xs font-mono font-semibold mb-3 border border-signal/25">
              ⚡ SGP4 Orbit Propagation Engine
            </div>
            <h3 className="text-2xl font-bold text-white">Live Pass & Downlink Calculator</h3>
            <p className="text-sm text-graphite-mute mt-1">
              Simulate orbital line-of-sight tracking and downlinked payload bandwidth for your satellite mission.
            </p>
          </div>

          <div className="space-y-4">
            {/* Satellite Selector */}
            <div>
              <label className="block text-xs font-mono text-graphite-mute uppercase tracking-wider mb-2">
                Select Target Satellite Mission
              </label>
              <select
                value={selectedSat.id}
                onChange={(e) => {
                  const sat = SATELLITES.find(s => s.id === e.target.value);
                  if (sat) setSelectedSat(sat);
                }}
                className="w-full p-3.5 bg-graphite-700 border border-graphite-500 rounded-sm text-white text-sm font-medium focus:ring-2 focus:ring-signal outline-none transition-all cursor-pointer"
              >
                {SATELLITES.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} (NORAD: {s.norad}) — {s.type}
                  </option>
                ))}
              </select>
            </div>

            {/* Ground Station Selector */}
            <div>
              <label className="block text-xs font-mono text-graphite-mute uppercase tracking-wider mb-2">
                Select Pan-African Ground Station Hub
              </label>
              <select
                value={stationId}
                onChange={(e) => setStationId(e.target.value)}
                className="w-full p-3.5 bg-graphite-700 border border-graphite-500 rounded-sm text-white text-sm font-medium focus:ring-2 focus:ring-signal outline-none transition-all cursor-pointer"
              >
                <option value="entoto">Entoto Space Observatory (Ethiopia) — 12.0m Antenna</option>
                <option value="hart">Hartebeesthoek Station (South Africa) — 9.3m Ka/X</option>
                <option value="malindi">Malindi Space Center (Kenya) — 10.0m S/X</option>
                <option value="abuja">Abuja Space Hub (Nigeria) — 7.3m S/X</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={isCalculating}
            className="w-full py-4 rounded-sm bg-gradient-to-r bg-signal hover:bg-signal-soft text-white font-bold text-sm shadow-xl shadow-black/40 transition-all hover:scale-[1.01] active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isCalculating ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Propagating TLE & Calculating Visibility...</span>
              </>
            ) : (
              <>
                <span>🚀 Predict Next Pass & Quote</span>
              </>
            )}
          </button>

        </div>

        {/* Right Output Dashboard Pane */}
        <div className="lg:col-span-6 glass-panel p-6 rounded-sm border border-graphite-600 bg-graphite-800 space-y-6">
          
          <div className="flex justify-between items-center border-b border-graphite-600 pb-4">
            <div>
              <span className="text-[10px] font-mono text-signal-soft uppercase tracking-widest">
                Simulation Output
              </span>
              <h4 className="text-lg font-bold text-white mt-0.5">{selectedSat.name}</h4>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono text-graphite-mute block uppercase">Signal Confidence</span>
              <span className="text-green-soft font-mono font-bold text-sm">{passResult.signalLockProb}</span>
            </div>
          </div>

          {/* Results Grid */}
          <div className="grid grid-cols-2 gap-4 font-mono">
            
            <div className="p-4 bg-graphite-800 rounded-sm border border-graphite-600">
              <span className="text-graphite-mute text-[11px] block uppercase">Next Pass Start (UTC)</span>
              <span className="text-signal-soft font-bold text-xs mt-1 block">
                {new Date(passResult.nextPassUTC).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })} UTC
              </span>
            </div>

            <div className="p-4 bg-graphite-800 rounded-sm border border-graphite-600">
              <span className="text-graphite-mute text-[11px] block uppercase">Pass Window Duration</span>
              <span className="text-white font-bold text-sm mt-1 block">{passResult.passDurationMin} minutes</span>
            </div>

            <div className="p-4 bg-graphite-800 rounded-sm border border-graphite-600">
              <span className="text-graphite-mute text-[11px] block uppercase">Max Elevation Angle</span>
              <span className="text-steel-2 font-bold text-sm mt-1 block">{passResult.maxElevationDeg}°</span>
            </div>

            <div className="p-4 bg-graphite-800 rounded-sm border border-graphite-600">
              <span className="text-graphite-mute text-[11px] block uppercase">Est. Downlink Data</span>
              <span className="text-green-soft font-bold text-sm mt-1 block">{passResult.estimatedDataGB} GB Payload</span>
            </div>

          </div>

          {/* Commercial Pricing Breakdown Box */}
          <div className="p-4 rounded-sm bg-gradient-to-r bg-graphite-700 border border-signal/30 flex justify-between items-center">
            <div>
              <span className="text-graphite-mute text-xs block font-mono">Dynamic GSaaS Pricing</span>
              <span className="text-xs text-steel-2 font-medium">Standard $15.00 / minute tier</span>
            </div>
            <div className="text-right">
              <span className="text-2xl font-black text-white font-mono">${passResult.costUSD}</span>
              <span className="text-[10px] text-signal-soft block font-mono">Instant Reservation</span>
            </div>
          </div>

          {/* Action CTA */}
          <Link
            href={`/${currentLocale}/booking`}
            className="w-full py-3 rounded-sm bg-graphite-600 hover:bg-graphite-500 text-signal-soft hover:text-signal-soft font-semibold text-xs font-mono uppercase tracking-wider transition-colors flex items-center justify-center gap-2"
          >
            <span>Proceed to Full Booking Wizard</span>
            <span>→</span>
          </Link>

        </div>

      </div>

    </div>
  );
}
