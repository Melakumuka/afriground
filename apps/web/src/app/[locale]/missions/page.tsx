"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useT } from "@/lib/useT";

type Mission = {
  id: string;
  name: string;
  norad_id: string;
  status: string;
  created_at: string;
  orbit_type?: string;
  frequency_band?: string;
};

const MOCK_MISSIONS: Mission[] = [
  { id: "sat-001", name: "AfriSat-1", norad_id: "55001", status: "ACTIVE", created_at: new Date(Date.now() - 86400000 * 30).toISOString(), orbit_type: "LEO", frequency_band: "S-Band" },
  { id: "sat-002", name: "NileStar-3", norad_id: "55042", status: "ACTIVE", created_at: new Date(Date.now() - 86400000 * 90).toISOString(), orbit_type: "SSO", frequency_band: "X-Band" },
  { id: "sat-003", name: "SaharaScan-2", norad_id: "55103", status: "COMMISSIONING", created_at: new Date(Date.now() - 86400000 * 7).toISOString(), orbit_type: "LEO", frequency_band: "UHF" },
  { id: "sat-004", name: "KenyaEO-1", norad_id: "55200", status: "DECOMMISSIONED", created_at: new Date(Date.now() - 86400000 * 365).toISOString(), orbit_type: "SSO", frequency_band: "Ka-Band" },
];

export default function MissionsIndex({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = use(params);
  const { t } = useT("Missions");
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchAllMissions() {
      try {
        const res = await fetch(`/api/platform/missions`);
        if (!res.ok) throw new Error("Failed to load missions");
        const json = await res.json();
        if (!json.ok) throw new Error(json.error || "Failed to load missions");
        if (json.data && json.data.length > 0) {
          setMissions(json.data);
        } else {
          setMissions(MOCK_MISSIONS);
        }
      } catch (err: any) {
        setMissions(MOCK_MISSIONS);
      } finally {
        setLoading(false);
      }
    }
    fetchAllMissions();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse flex items-center gap-3">
          <span className="w-3 h-3 rounded-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)]"></span>
          {t("loading", "Loading Spacecraft...", "LOADING SPACECRAFT...")}
        </div>
      </div>
    );
  }

  const statusColors: Record<string, { bg: string; text: string; dot: string }> = {
    ACTIVE: { bg: "bg-green-500/15", text: "text-green-400", dot: "bg-green-400" },
    COMMISSIONING: { bg: "bg-blue-500/15", text: "text-blue-400", dot: "bg-blue-400" },
    DECOMMISSIONED: { bg: "bg-white/10", text: "text-white/50", dot: "bg-white/40" },
    SUSPENDED: { bg: "bg-orange-500/15", text: "text-orange-400", dot: "bg-orange-400" },
  };

  return (
    <div className="min-h-screen bg-black text-white/90 p-8 relative overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute top-[-15%] right-[-10%] w-[45%] h-[45%] bg-emerald-600/15 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-20%] left-[-5%] w-[50%] h-[50%] bg-teal-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute top-[50%] right-[20%] w-[25%] h-[25%] bg-cyan-500/8 rounded-full blur-[100px] pointer-events-none mix-blend-screen animate-pulse"></div>

      <div className="max-w-6xl mx-auto space-y-10 relative z-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-emerald-200 to-teal-400 mb-3 drop-shadow-sm">
              {t("title", "Spacecraft & Missions", "SPACECRAFT & MISSIONS")}
            </h1>
            <div className="flex items-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 shadow-[0_0_10px_rgba(52,211,153,0.8)]"></span>
              </span>
              <p className="text-emerald-400 text-sm font-mono tracking-widest uppercase">
                {t("subtitle", "Orbital Asset Registry", "ORBITAL ASSET REGISTRY")}
              </p>
            </div>
          </div>
          <Link
            href={`/${locale}/missions/new`}
            className="px-8 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 transition-all rounded-full text-sm font-bold tracking-widest uppercase text-white shadow-[0_0_25px_rgba(52,211,153,0.4)] flex items-center gap-2 group"
          >
            <svg className="w-5 h-5 group-hover:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path></svg>
            {t("add", "Add Spacecraft", "ADD SPACECRAFT")}
          </Link>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total Assets", value: missions.length, color: "text-white" },
            { label: "Active", value: missions.filter(m => m.status === "ACTIVE").length, color: "text-green-400" },
            { label: "Commissioning", value: missions.filter(m => m.status === "COMMISSIONING").length, color: "text-blue-400" },
            { label: "Decommissioned", value: missions.filter(m => m.status === "DECOMMISSIONED").length, color: "text-white/50" },
          ].map((stat, i) => (
            <div key={i} className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-colors">
              <div className="text-[10px] uppercase tracking-widest text-white/40 mb-2 font-semibold">{stat.label}</div>
              <div className={`text-3xl font-extrabold font-mono ${stat.color}`}>{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Spacecraft Grid */}
        {missions.length === 0 ? (
          <div className="border border-dashed border-white/10 rounded-3xl p-16 text-center backdrop-blur-sm bg-black/20">
            <svg className="w-12 h-12 mx-auto mb-4 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"></path></svg>
            <h3 className="text-xl font-bold mb-2">{t("empty_title", "No Spacecraft Registered", "No Spacecraft Registered")}</h3>
            <p className="text-white/40 mb-8">{t("empty_desc", "Register a new satellite to begin planning contacts.", "Register a new satellite to begin planning contacts.")}</p>
            <Link
              href={`/${locale}/missions/new`}
              className="px-8 py-3 border border-white/20 hover:border-emerald-500/50 text-white hover:text-emerald-300 font-bold text-sm transition-all inline-block rounded-full tracking-widest uppercase"
            >
              {t("add", "Add Spacecraft", "ADD SPACECRAFT")}
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {missions.map((m, index) => {
              const sColor = statusColors[m.status] || statusColors.ACTIVE;
              return (
                <div
                  key={m.id}
                  className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8 hover:border-emerald-500/40 transition-all duration-300 group hover:-translate-y-1 shadow-[0_0_20px_rgba(0,0,0,0.5)] hover:shadow-[0_0_30px_rgba(52,211,153,0.15)] animate-in fade-in slide-in-from-bottom-4"
                  style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'both' }}
                >
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="text-2xl font-extrabold tracking-tight group-hover:text-emerald-300 transition-colors">{m.name}</h3>
                      <p className="text-xs text-white/30 font-mono mt-1">{m.id}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${sColor.dot} ${m.status === 'ACTIVE' ? 'animate-pulse shadow-[0_0_6px_rgba(52,211,153,0.8)]' : ''}`}></span>
                      <span className={`px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-full ${sColor.bg} ${sColor.text} border border-current/20`}>
                        {m.status}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-6">
                    <div className="bg-white/5 rounded-xl p-3">
                      <span className="text-[10px] text-white/40 uppercase tracking-widest block mb-1">NORAD ID</span>
                      <span className="font-mono text-emerald-400 font-bold">{m.norad_id}</span>
                    </div>
                    <div className="bg-white/5 rounded-xl p-3">
                      <span className="text-[10px] text-white/40 uppercase tracking-widest block mb-1">Orbit</span>
                      <span className="font-mono text-white/80 font-bold">{m.orbit_type || "LEO"}</span>
                    </div>
                    <div className="bg-white/5 rounded-xl p-3">
                      <span className="text-[10px] text-white/40 uppercase tracking-widest block mb-1">Band</span>
                      <span className="font-mono text-white/80 font-bold">{m.frequency_band || "S-Band"}</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center pt-5 border-t border-white/5">
                    <span className="text-xs text-white/30 font-mono">
                      Registered {new Date(m.created_at).toLocaleDateString()}
                    </span>
                    <Link
                      href={`/${locale}/booking`}
                      className="flex items-center gap-1 text-sm font-bold text-white/50 group-hover:text-emerald-400 transition-colors"
                    >
                      Plan Contact
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path></svg>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
