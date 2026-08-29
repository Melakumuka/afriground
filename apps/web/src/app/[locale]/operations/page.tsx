"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useT } from "@/lib/useT";

type Job = {
  id: string;
  status: string;
  priority: number;
  tx_requested: boolean;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  contact_id?: string;
};

export default function OperationsDashboard({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = use(params);
  const { t } = useT("Operations");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchJobs() {
      try {
        const res = await fetch(`/api/platform/contact/jobs`);
        if (!res.ok) {
          throw new Error("Failed to load active jobs");
        }
        const json = await res.json();
        if (!json.ok) throw new Error(json.error || "Failed to load active jobs");
        setJobs(json.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load active jobs");
      } finally {
        setLoading(false);
      }
    }
    fetchJobs();
    
    // Auto-refresh every 10 seconds for real-time tracking
    const interval = setInterval(fetchJobs, 10000);
    return () => clearInterval(interval);
  }, []);

  const columns = ["QUEUED", "DISPATCHED", "EXECUTING", "COMPLETED", "FAILED"];

  if (loading && jobs.length === 0) {
    return (
      <div className="min-h-screen bg-graphite text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse">{t("loading", "Loading Operations Board...", "LOADING OPERATIONS BOARD...")}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-graphite text-white/90 p-8">
      <div className="max-w-[1600px] mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">
            {t("title", "Operations Command Center", "OPERATIONS COMMAND CENTER")}
          </h1>
          <p className="text-white/50 text-sm font-mono flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-signal animate-pulse"></span>
            {t("subtitle", "Live Job Tracking", "LIVE JOB TRACKING")}
          </p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm">
            {error}
          </div>
        )}

        {/* Kanban Board */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 overflow-x-auto pb-8">
          {columns.map(status => {
            const columnJobs = jobs.filter(j => j.status === status).sort((a, b) => 
              new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
            );
            
            return (
              <div key={status} className="flex flex-col min-w-[300px]">
                <div className="flex justify-between items-center mb-4 border-b border-white/10 pb-2">
                  <h3 className="text-sm font-semibold tracking-wide text-white/70">
                    {status}
                  </h3>
                  <span className="text-xs font-mono bg-white/5 px-2 py-0.5 rounded-full text-white/50">
                    {columnJobs.length}
                  </span>
                </div>
                
                <div className="flex-1 space-y-4">
                  {columnJobs.map(job => (
                    <Link 
                      key={job.id} 
                      href={`/${locale}/operations/jobs/${job.id}`}
                      className="block group"
                    >
                      <div className="bg-white/5 hover:bg-white/10 border border-white/10 hover:border-signal/50 transition-colors p-4 rounded-xl cursor-pointer">
                        <div className="flex justify-between items-start mb-3">
                          <span className="text-xs font-mono text-white/40 truncate w-32" title={job.id}>
                            {job.id.substring(0, 8)}...
                          </span>
                          {job.tx_requested && (
                            <span className="text-[10px] font-bold bg-orange-500/20 text-orange-400 px-1.5 py-0.5 rounded uppercase">
                              TX
                            </span>
                          )}
                        </div>
                        
                        <div className="text-sm text-white/80 font-medium mb-3">
                          {t("priority", "Priority", "Priority")}: {job.priority}
                        </div>
                        
                        <div className="flex justify-between items-center text-xs text-white/50">
                          <span>
                            {new Date(job.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          <span className="opacity-0 group-hover:opacity-100 transition-opacity text-signal">
                            {t("view", "View", "View")} →
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                  
                  {columnJobs.length === 0 && (
                    <div className="border border-dashed border-white/5 rounded-xl h-24 flex items-center justify-center">
                      <span className="text-xs text-white/30 uppercase tracking-wider">{t("empty", "No jobs", "NO JOBS")}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
