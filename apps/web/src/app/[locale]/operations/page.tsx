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
        
        // If no jobs are returned, use premium mock data to showcase the UI
        if (json.data && json.data.length > 0) {
          setJobs(json.data);
        } else {
          setJobs([
            { id: "mock-job-123", status: "QUEUED", priority: 8, tx_requested: false, started_at: null, completed_at: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
            { id: "mock-job-456", status: "DISPATCHED", priority: 5, tx_requested: true, started_at: null, completed_at: null, created_at: new Date().toISOString(), updated_at: new Date(Date.now() - 60000).toISOString() },
            { id: "mock-job-789", status: "EXECUTING", priority: 9, tx_requested: true, started_at: new Date().toISOString(), completed_at: null, created_at: new Date(Date.now() - 120000).toISOString(), updated_at: new Date().toISOString() },
            { id: "mock-job-012", status: "COMPLETED", priority: 2, tx_requested: false, started_at: new Date(Date.now() - 360000).toISOString(), completed_at: new Date().toISOString(), created_at: new Date(Date.now() - 400000).toISOString(), updated_at: new Date().toISOString() }
          ]);
        }
      } catch (err: any) {
        setError(err.message);
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
    <div className="min-h-screen bg-black text-white/90 p-8 relative overflow-hidden">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-indigo-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute top-[40%] left-[30%] w-[30%] h-[30%] bg-cyan-500/10 rounded-full blur-[100px] pointer-events-none mix-blend-screen animate-pulse"></div>

      <div className="max-w-[1600px] mx-auto space-y-10 relative z-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-200 to-indigo-400 mb-3 drop-shadow-sm">
              {t("title", "Operations Command Center", "OPERATIONS COMMAND CENTER")}
            </h1>
            <div className="flex items-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)]"></span>
              </span>
              <p className="text-cyan-400 text-sm font-mono tracking-widest uppercase shadow-cyan-500/50">
                {t("subtitle", "Live Job Tracking", "LIVE JOB TRACKING")}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-sm font-mono bg-white/5 px-4 py-2 rounded-full border border-white/10 backdrop-blur-md">
            <span className="text-white/50">Active Jobs:</span>
            <span className="text-white font-bold">{jobs.filter(j => j.status !== 'COMPLETED' && j.status !== 'FAILED').length}</span>
          </div>
        </div>

        {error && (
          <div className="bg-red-950/50 border border-red-500/50 text-red-300 p-4 rounded-xl text-sm backdrop-blur-md shadow-[0_0_15px_rgba(239,68,68,0.2)] flex items-center gap-3">
            <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            {error}
          </div>
        )}

        {/* Kanban Board */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 overflow-x-auto pb-12 snap-x">
          {columns.map((status, index) => {
            const columnJobs = jobs.filter(j => j.status === status).sort((a, b) => 
              new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
            );
            
            // Premium status colors
            const statusColors: Record<string, { border: string, bg: string, text: string, dot: string, glow: string }> = {
              "QUEUED": { border: "border-white/20", bg: "bg-white/5", text: "text-white/70", dot: "bg-white/50", glow: "hover:border-white/40 shadow-[0_0_15px_rgba(255,255,255,0.05)]" },
              "DISPATCHED": { border: "border-blue-500/30", bg: "bg-blue-500/10", text: "text-blue-300", dot: "bg-blue-400", glow: "hover:border-blue-400/60 shadow-[0_0_15px_rgba(59,130,246,0.15)]" },
              "EXECUTING": { border: "border-indigo-500/40", bg: "bg-indigo-500/10", text: "text-indigo-300", dot: "bg-indigo-400", glow: "hover:border-indigo-400/60 shadow-[0_0_20px_rgba(99,102,241,0.25)]" },
              "COMPLETED": { border: "border-green-500/30", bg: "bg-green-500/10", text: "text-green-300", dot: "bg-green-400", glow: "hover:border-green-400/60 shadow-[0_0_15px_rgba(34,197,94,0.15)]" },
              "FAILED": { border: "border-red-500/30", bg: "bg-red-500/10", text: "text-red-300", dot: "bg-red-400", glow: "hover:border-red-400/60 shadow-[0_0_15px_rgba(239,68,68,0.15)]" },
            };
            const colStyle = statusColors[status] || statusColors["QUEUED"];

            return (
              <div key={status} className="flex flex-col min-w-[320px] snap-center animate-in fade-in slide-in-from-bottom-4" style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'both' }}>
                <div className={`flex justify-between items-center mb-4 border-b ${colStyle.border} pb-3`}>
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${colStyle.dot} ${status === 'EXECUTING' ? 'animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.8)]' : ''}`}></span>
                    <h3 className={`text-sm font-bold tracking-widest uppercase ${colStyle.text}`}>
                      {status}
                    </h3>
                  </div>
                  <span className={`text-xs font-mono px-2.5 py-0.5 rounded-full backdrop-blur-md ${colStyle.bg} ${colStyle.border} border ${colStyle.text}`}>
                    {columnJobs.length}
                  </span>
                </div>
                
                <div className="flex-1 space-y-4">
                  {columnJobs.map((job, jIndex) => (
                    <Link 
                      key={job.id} 
                      href={`/${locale}/operations/jobs/${job.id}`}
                      className="block group"
                    >
                      <div className={`bg-black/40 backdrop-blur-xl border ${colStyle.border} rounded-2xl p-5 cursor-pointer transition-all duration-300 transform group-hover:-translate-y-1 ${colStyle.glow} animate-in fade-in zoom-in-95`} style={{ animationDelay: `${(index * 100) + (jIndex * 50)}ms`, animationFillMode: 'both' }}>
                        
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex flex-col">
                            <span className="text-[10px] uppercase tracking-widest text-white/40 mb-1">Job ID</span>
                            <span className="text-sm font-mono text-white/90 truncate w-32 font-medium bg-white/5 px-2 py-0.5 rounded" title={job.id}>
                              {job.id.substring(0, 8)}
                            </span>
                          </div>
                          {job.tx_requested && (
                            <span className="text-[10px] font-extrabold bg-gradient-to-r from-orange-500/30 to-red-500/30 border border-orange-500/50 text-orange-300 px-2 py-1 rounded shadow-[0_0_10px_rgba(249,115,22,0.3)] uppercase tracking-wider">
                              TX Active
                            </span>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2 mb-4">
                          <div className="bg-white/5 rounded-lg p-2 flex flex-col justify-center">
                            <span className="text-[10px] text-white/40 uppercase tracking-wider mb-0.5">{t("priority", "Priority", "Priority")}</span>
                            <div className="flex items-center gap-1">
                              <span className="text-white/90 font-bold">{job.priority}</span>
                              {job.priority > 7 && <svg className="w-3 h-3 text-red-400" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd"></path></svg>}
                            </div>
                          </div>
                          <div className="bg-white/5 rounded-lg p-2 flex flex-col justify-center">
                            <span className="text-[10px] text-white/40 uppercase tracking-wider mb-0.5">Updated</span>
                            <span className="text-white/80 text-xs font-mono">
                              {new Date(job.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex justify-between items-center text-xs pt-3 border-t border-white/5">
                          <span className={`px-2 py-1 rounded bg-white/5 ${colStyle.text} text-[10px] font-bold tracking-wider`}>
                            {status}
                          </span>
                          <div className="flex items-center gap-1 opacity-50 group-hover:opacity-100 transition-opacity">
                            <span className="text-white font-medium">{t("view_details", "View Details", "View Details")}</span>
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path></svg>
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                  
                  {columnJobs.length === 0 && (
                    <div className={`border border-dashed ${colStyle.border} bg-black/20 rounded-2xl h-32 flex flex-col items-center justify-center backdrop-blur-sm opacity-50`}>
                      <svg className="w-6 h-6 mb-2 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path></svg>
                      <span className="text-xs text-white/30 uppercase tracking-widest font-medium">{t("empty", "No jobs", "NO JOBS")}</span>
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
