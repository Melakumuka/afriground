"use client";

import { useState } from "react";
import Link from "next/link";

type GroundStationNode = {
  id: string;
  name: string;
  country: string;
  lat: number;
  lng: number;
  dishSize: string;
  bands: string[];
  gtPerformance: string;
  minElevation: string;
  status: "Operational" | "Maintenance";
  description: string;
  topCoords: { top: string; left: string }; // Position percentage on graphic map
};

const STATIONS: GroundStationNode[] = [
  {
    id: "entoto",
    name: "Entoto Space Observatory (ENT-1)",
    country: "Ethiopia 🇪🇹",
    lat: 9.076,
    lng: 38.740,
    dishSize: "12.0m Parabolic",
    bands: ["S-band", "X-band"],
    gtPerformance: "32.5 dB/K @ 8.2 GHz",
    minElevation: "5.0°",
    status: "Operational",
    description: "High-altitude equatorial hub providing high-elevation pass coverage over East and Central Africa with ultra-clear sky conditions.",
    topCoords: { top: "45%", left: "68%" }
  },
  {
    id: "hart",
    name: "Hartebeesthoek Space Station (HBK-1)",
    country: "South Africa 🇿🇦",
    lat: -25.886,
    lng: 27.707,
    dishSize: "9.3m Dual Feed",
    bands: ["S-band", "X-band", "Ka-band"],
    gtPerformance: "34.1 dB/K @ 26.0 GHz",
    minElevation: "3.5°",
    status: "Operational",
    description: "Southern hemisphere deep space and LEO downlink hub with multi-band Ka-band capability and fiber cloud backhaul.",
    topCoords: { top: "82%", left: "56%" }
  },
  {
    id: "malindi",
    name: "Malindi Space Center (MAL-1)",
    country: "Kenya 🇰🇪",
    lat: -2.996,
    lng: 40.194,
    dishSize: "10.0m Prime Focus",
    bands: ["S-band", "X-band"],
    gtPerformance: "30.8 dB/K @ 8.1 GHz",
    minElevation: "4.0°",
    status: "Operational",
    description: "Coastal Indian Ocean equatorial tracking station ideal for launch support, early orbit phase (LEOP), and LEO data downlinks.",
    topCoords: { top: "56%", left: "70%" }
  },
  {
    id: "abuja",
    name: "Abuja Regional Gateway (ABJ-1)",
    country: "Nigeria 🇳🇬",
    lat: 9.076,
    lng: 7.398,
    dishSize: "7.3m Az/El Quad",
    bands: ["S-band", "X-band"],
    gtPerformance: "28.5 dB/K @ 8.0 GHz",
    minElevation: "5.0°",
    status: "Operational",
    description: "West Africa hub optimized for Earth observation satellite data downlink, emergency payload stream, and weather monitoring.",
    topCoords: { top: "45%", left: "42%" }
  },
  {
    id: "cairo",
    name: "Cairo North Gateway (CAI-1)",
    country: "Egypt 🇪🇬",
    lat: 30.044,
    lng: 31.235,
    dishSize: "11.2m Cassegrain",
    bands: ["X-band", "Ka-band"],
    gtPerformance: "33.0 dB/K @ 8.4 GHz",
    minElevation: "3.0°",
    status: "Operational",
    description: "North African Mediterranean gateway linking European orbital passes with African ground backhaul networks.",
    topCoords: { top: "22%", left: "62%" }
  },
  {
    id: "dakar",
    name: "Dakar Atlantic Hub (DKR-1)",
    country: "Senegal 🇸🇳",
    lat: 14.716,
    lng: -17.467,
    dishSize: "5.5m Fast Steer",
    bands: ["S-band", "UHF/VHF"],
    gtPerformance: "24.2 dB/K @ 2.2 GHz",
    minElevation: "5.0°",
    status: "Operational",
    description: "Westernmost African ground terminal providing early detection and contact passes over the Atlantic Ocean corridor.",
    topCoords: { top: "40%", left: "22%" }
  }
];

export default function StationNetworkMap({ currentLocale }: { currentLocale: string }) {
  const [selectedStation, setSelectedStation] = useState<GroundStationNode>(STATIONS[0]);

  return (
    <div className="w-full space-y-8">
      
      {/* Station Selector Pill Bar */}
      <div className="flex flex-wrap justify-center gap-2">
        {STATIONS.map((station) => {
          const isSelected = selectedStation.id === station.id;
          return (
            <button
              key={station.id}
              onClick={() => setSelectedStation(station)}
              className={`px-4 py-2.5 rounded-xl text-xs font-mono transition-all flex items-center gap-2 ${
                isSelected
                  ? "bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-400/50 shadow-lg shadow-cyan-500/10 scale-105"
                  : "bg-slate-900/80 text-slate-400 border border-slate-800 hover:text-white hover:border-slate-700"
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${isSelected ? 'bg-cyan-400 animate-pulse' : 'bg-emerald-500'}`} />
              <span className="font-semibold">{station.name.split(" ")[0]}</span>
              <span className="opacity-70">({station.country.split(" ")[1]})</span>
            </button>
          );
        })}
      </div>

      {/* Main Map & Card Display Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        
        {/* Left Column: Visual Interactive Graphic Map */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-2xl relative min-h-[420px] flex flex-col justify-between overflow-hidden border border-cyan-500/10">
          
          {/* Radar background effect */}
          <div className="absolute inset-0 opacity-15 pointer-events-none flex items-center justify-center">
            <div className="w-96 h-96 border border-cyan-500/30 rounded-full animate-pulse" />
            <div className="w-64 h-64 border border-cyan-500/30 rounded-full absolute" />
            <div className="w-32 h-32 border border-cyan-500/40 rounded-full absolute" />
            <div className="w-full h-[1px] bg-cyan-500/20 absolute" />
            <div className="h-full w-[1px] bg-cyan-500/20 absolute" />
          </div>

          {/* Continent Map Graphic Header */}
          <div className="flex justify-between items-center z-10">
            <div>
              <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">
                Interactive Pan-African Node Map
              </span>
              <h3 className="text-lg font-bold text-white">Live Ground Antenna Telemetry</h3>
            </div>
            <div className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[11px] font-mono text-emerald-400 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              6 Active Nodes Highlighted
            </div>
          </div>

          {/* Interactive Continent Node Pins */}
          <div className="relative w-full h-[320px] bg-slate-950/60 rounded-xl border border-slate-800/80 my-4 overflow-hidden">
            {/* Subtle Grid overlay */}
            <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] opacity-40" />

            {/* Map Node Buttons */}
            {STATIONS.map((st) => {
              const isSelected = st.id === selectedStation.id;
              return (
                <button
                  key={st.id}
                  onClick={() => setSelectedStation(st)}
                  style={{ top: st.topCoords.top, left: st.topCoords.left }}
                  className="absolute transform -translate-x-1/2 -translate-y-1/2 group z-20"
                >
                  <div className="relative flex items-center justify-center">
                    {/* Ring ping when selected */}
                    {isSelected && (
                      <span className="absolute w-8 h-8 rounded-full bg-cyan-400/30 animate-ping" />
                    )}
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center border transition-all ${
                      isSelected 
                        ? "bg-cyan-400 border-white shadow-lg shadow-cyan-400/50 scale-125"
                        : "bg-slate-900 border-cyan-500/50 group-hover:scale-110 group-hover:border-cyan-400"
                    }`}>
                      <div className={`w-2 h-2 rounded-full ${isSelected ? "bg-slate-950" : "bg-cyan-400"}`} />
                    </div>

                    {/* Tooltip Label */}
                    <div className={`absolute top-6 left-1/2 transform -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded text-[10px] font-mono transition-all ${
                      isSelected
                        ? "bg-cyan-950 text-cyan-300 border border-cyan-400/40 shadow-lg z-30 font-bold"
                        : "bg-slate-900/90 text-slate-400 border border-slate-800 opacity-80 group-hover:opacity-100"
                    }`}>
                      {st.name.split(" ")[0]}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="flex justify-between items-center text-xs text-slate-500 font-mono z-10">
            <span>Click any node pin to view station specs</span>
            <span>Coverage: 35°N to 35°S</span>
          </div>

        </div>

        {/* Right Column: Selected Station Specifications Panel */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-2xl flex flex-col justify-between border border-cyan-500/20 shadow-xl bg-slate-900/90">
          
          <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-start border-b border-slate-800 pb-4">
              <div>
                <span className="text-xs font-mono text-cyan-400 uppercase tracking-widest">
                  Station Profile
                </span>
                <h3 className="text-xl font-bold text-white mt-1">{selectedStation.name}</h3>
                <p className="text-xs text-slate-400 mt-0.5">{selectedStation.country}</p>
              </div>
              <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-xs font-semibold rounded-full">
                {selectedStation.status}
              </span>
            </div>

            {/* Description */}
            <p className="text-sm text-slate-300 leading-relaxed">
              {selectedStation.description}
            </p>

            {/* Spec Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Antenna Size</span>
                <span className="text-white font-bold text-sm">{selectedStation.dishSize}</span>
              </div>
              <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">G/T Figure of Merit</span>
                <span className="text-cyan-400 font-bold text-sm">{selectedStation.gtPerformance}</span>
              </div>
              <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Min Elevation</span>
                <span className="text-white font-bold text-sm">{selectedStation.minElevation}</span>
              </div>
              <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Coordinates</span>
                <span className="text-white font-bold text-sm">
                  {selectedStation.lat.toFixed(2)}°, {selectedStation.lng.toFixed(2)}°
                </span>
              </div>
            </div>

            {/* Frequency Bands Badges */}
            <div>
              <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block mb-2">
                Supported Frequency Bands
              </span>
              <div className="flex flex-wrap gap-2">
                {selectedStation.bands.map((b) => (
                  <span
                    key={b}
                    className="px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-mono text-xs font-bold"
                  >
                    📡 {b}
                  </span>
                ))}
              </div>
            </div>

          </div>

          {/* Action CTAs */}
          <div className="pt-6 border-t border-slate-800/80 flex gap-3">
            <Link
              href={`/${currentLocale}/booking`}
              className="flex-1 py-3 text-center rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/20 transition-all hover:scale-[1.02]"
            >
              Book Pass on {selectedStation.name.split(" ")[0]}
            </Link>
            <Link
              href={`/${currentLocale}/station`}
              className="px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold transition-colors"
            >
              Telemetry Stream
            </Link>
          </div>

        </div>

      </div>

    </div>
  );
}
