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
};

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
        setMissions(json.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load missions");
      } finally {
        setLoading(false);
      }
    }
    fetchAllMissions();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-graphite text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse">{t("loading", "Loading Spacecraft...", "LOADING SPACECRAFT...")}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-graphite text-white/90 p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex justify-between items-end border-b border-white/10 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">
              {t("title", "Spacecraft & Missions", "SPACECRAFT & MISSIONS")}
            </h1>
            <p className="text-white/50 text-sm font-mono">
              {t("subtitle", "Manage your orbital assets and mission profiles", "Manage your orbital assets and mission profiles")}
            </p>
          </div>
          <Link
            href={`/${locale}/missions/new`}
            className="px-6 py-2.5 bg-white text-black font-semibold text-sm hover:bg-white/90 transition-colors"
          >
            + {t("add", "Add Spacecraft", "ADD SPACECRAFT")}
          </Link>
        </div>

        {error ? (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm">
            {error}
          </div>
        ) : missions.length === 0 ? (
          <div className="border border-dashed border-white/10 rounded-2xl p-12 text-center">
            <h3 className="text-xl font-semibold mb-2">{t("empty_title", "No Spacecraft Registered", "No Spacecraft Registered")}</h3>
            <p className="text-white/50 mb-6">{t("empty_desc", "Register a new satellite to begin planning contacts.", "Register a new satellite to begin planning contacts.")}</p>
            <Link
              href={`/${locale}/missions/new`}
              className="px-6 py-2.5 border border-white/20 hover:border-white/50 text-white font-semibold text-sm transition-colors inline-block"
            >
              {t("add", "Add Spacecraft", "ADD SPACECRAFT")}
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {missions.map((m) => (
              <div key={m.id} className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-signal/50 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold">{m.name}</h3>
                  <span className={`px-2 py-1 text-[10px] font-bold uppercase rounded ${
                    m.status === "ACTIVE" ? "bg-green-500/20 text-green-400" : "bg-white/10 text-white/50"
                  }`}>
                    {m.status}
                  </span>
                </div>
                
                <div className="space-y-2 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-white/40">NORAD ID</span>
                    <span className="font-mono text-signal">{m.norad_id}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-white/40">Registered</span>
                    <span className="font-mono">{new Date(m.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10 flex justify-between items-center">
                  <Link 
                    href={`/${locale}/booking`} 
                    className="text-sm font-semibold text-white/70 hover:text-white transition-colors"
                  >
                    Plan Contact →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
