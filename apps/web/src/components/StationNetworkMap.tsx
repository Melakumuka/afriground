"use client";

import { useState } from "react";
import Link from "next/link";
import { STATIONS, type GroundStationNode } from "@/data/stations";

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
              className={`px-4 py-2.5 rounded-sm text-xs font-mono transition-all flex items-center gap-2 ${
                isSelected
                  ? "bg-gradient-to-r bg-signal/15 text-signal-soft border border-signal/50 shadow-lg shadow-black/30 scale-105"
                  : "bg-graphite-700/80 text-graphite-mute border border-graphite-600 hover:text-white hover:border-graphite-500"
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${isSelected ? 'bg-signal animate-pulse' : 'bg-green'}`} />
              <span className="font-semibold">{station.name.split(" ")[0]}</span>
              <span className="opacity-70">({station.country.split(" ")[1]})</span>
            </button>
          );
        })}
      </div>

      {/* Main Map & Card Display Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        
        {/* Left Column: Visual Interactive Graphic Map */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-sm relative min-h-[420px] flex flex-col justify-between overflow-hidden border border-signal/15">
          
          {/* Radar background effect */}
          <div className="absolute inset-0 opacity-15 pointer-events-none flex items-center justify-center">
            <div className="w-96 h-96 border border-signal/30 rounded-full animate-pulse" />
            <div className="w-64 h-64 border border-signal/30 rounded-full absolute" />
            <div className="w-32 h-32 border border-signal/40 rounded-full absolute" />
            <div className="w-full h-[1px] bg-signal/20 absolute" />
            <div className="h-full w-[1px] bg-signal/20 absolute" />
          </div>

          {/* Continent Map Graphic Header */}
          <div className="flex justify-between items-center z-10">
            <div>
              <span className="text-xs font-mono text-signal-soft uppercase tracking-wider">
                Interactive Pan-African Node Map
              </span>
              <h3 className="text-lg font-bold text-white">Live Ground Antenna Telemetry</h3>
            </div>
            <div className="px-3 py-1 bg-green/15 border border-green/30 rounded-full text-[11px] font-mono text-green-soft flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-soft animate-ping" />
              6 Active Nodes Highlighted
            </div>
          </div>

          {/* Interactive Continent Node Pins */}
          <div className="relative w-full h-[320px] bg-graphite-800/70 rounded-sm border border-graphite-600/80 my-4 overflow-hidden">
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
                      <span className="absolute w-8 h-8 rounded-full bg-signal/30 animate-ping" />
                    )}
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center border transition-all ${
                      isSelected 
                        ? "bg-signal border-white shadow-lg shadow-black/50 scale-125"
                        : "bg-graphite-700 border-signal/50 group-hover:scale-110 group-hover:border-signal"
                    }`}>
                      <div className={`w-2 h-2 rounded-full ${isSelected ? "bg-graphite" : "bg-signal"}`} />
                    </div>

                    {/* Tooltip Label */}
                    <div className={`absolute top-6 left-1/2 transform -translate-x-1/2 whitespace-nowrap px-2.5 py-1 rounded text-[10px] font-mono transition-all ${
                      isSelected
                        ? "bg-graphite text-signal-soft border border-signal/40 shadow-lg z-30 font-bold"
                        : "bg-graphite-800 text-graphite-mute border border-graphite-600 opacity-80 group-hover:opacity-100"
                    }`}>
                      {st.name.split(" ")[0]}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="flex justify-between items-center text-xs text-graphite-mute font-mono z-10">
            <span>Click any node pin to view station specs</span>
            <span>Coverage: 35°N to 35°S</span>
          </div>

        </div>

        {/* Right Column: Selected Station Specifications Panel */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-sm flex flex-col justify-between border border-signal/25 shadow-xl bg-graphite-800">
          
          <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-start border-b border-graphite-600 pb-4">
              <div>
                <span className="text-xs font-mono text-signal-soft uppercase tracking-widest">
                  Station Profile
                </span>
                <h3 className="text-xl font-bold text-white mt-1">{selectedStation.name}</h3>
                <p className="text-xs text-graphite-mute mt-0.5">{selectedStation.country}</p>
              </div>
              <span className="px-3 py-1 bg-green/15 border border-green/30 text-green-soft font-mono text-xs font-semibold rounded-full">
                {selectedStation.status}
              </span>
            </div>

            {/* Description */}
            <p className="text-sm text-steel-2 leading-relaxed">
              {selectedStation.description}
            </p>

            {/* Spec Metrics Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 bg-graphite-800/80 rounded-sm border border-graphite-600">
                <span className="text-graphite-mute block text-[10px] uppercase">Antenna Size</span>
                <span className="text-white font-bold text-sm">{selectedStation.dishSize}</span>
              </div>
              <div className="p-3 bg-graphite-800/80 rounded-sm border border-graphite-600">
                <span className="text-graphite-mute block text-[10px] uppercase">G/T Figure of Merit</span>
                <span className="text-signal-soft font-bold text-sm">{selectedStation.gtPerformance}</span>
              </div>
              <div className="p-3 bg-graphite-800/80 rounded-sm border border-graphite-600">
                <span className="text-graphite-mute block text-[10px] uppercase">Min Elevation</span>
                <span className="text-white font-bold text-sm">{selectedStation.minElevation}</span>
              </div>
              <div className="p-3 bg-graphite-800/80 rounded-sm border border-graphite-600">
                <span className="text-graphite-mute block text-[10px] uppercase">Coordinates</span>
                <span className="text-white font-bold text-sm">
                  {selectedStation.lat.toFixed(2)}°, {selectedStation.lng.toFixed(2)}°
                </span>
              </div>
            </div>

            {/* Frequency Bands Badges */}
            <div>
              <span className="text-xs font-mono text-graphite-mute uppercase tracking-wider block mb-2">
                Supported Frequency Bands
              </span>
              <div className="flex flex-wrap gap-2">
                {selectedStation.bands.map((b) => (
                  <span
                    key={b}
                    className="px-3 py-1.5 rounded-sm bg-steel/10 border border-steel/30 text-steel-2 font-mono text-xs font-bold"
                  >
                    📡 {b}
                  </span>
                ))}
              </div>
            </div>

          </div>

          {/* Action CTAs */}
          <div className="pt-6 border-t border-graphite-600/80 flex gap-3">
            <Link
              href={`/${currentLocale}/booking`}
              className="flex-1 py-3 text-center rounded-sm bg-gradient-to-r bg-signal hover:bg-signal-soft text-white font-semibold text-sm shadow-lg shadow-black/40 transition-all hover:scale-[1.02]"
            >
              Book Pass on {selectedStation.name.split(" ")[0]}
            </Link>
            <Link
              href={`/${currentLocale}/station`}
              className="px-4 py-3 rounded-sm bg-graphite-600 hover:bg-graphite-500 text-ink text-sm font-semibold transition-colors"
            >
              Telemetry Stream
            </Link>
          </div>

        </div>

      </div>

    </div>
  );
}
