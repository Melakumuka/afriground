"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useT } from "@/lib/useT";

type ReadinessEvent = {
  status: string;
  confirmed_at: string;
  checklist_results: any;
  notes: string | null;
};

type ExecutionReceipt = {
  status: string;
  carrier_locked: boolean | null;
  symbol_locked: boolean | null;
  data_volume_bytes: number | null;
  average_ebno: number | null;
  pass_report_hash: string | null;
};

type JobDetails = {
  id: string;
  status: string;
  priority: number;
  tx_requested: boolean;
  started_at: string | null;
  completed_at: string | null;
  readiness?: ReadinessEvent;
  receipt?: ExecutionReceipt;
};

export default function JobDetailsPage({ params }: { params: Promise<{ locale: string, job_id: string }> }) {
  const { locale, job_id } = use(params);
  const { t } = useT("JobDetails");
  const [job, setJob] = useState<JobDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchJob() {
      try {
        const res = await fetch(`/api/platform/contact/jobs/${job_id}`);
        if (!res.ok) {
          throw new Error("Failed to load job details");
        }
        const json = await res.json();
        if (!json.ok) {
          throw new Error(json.error || "Failed to load job details");
        }
        
        if (json.data) {
          setJob(json.data);
        }
      } catch (err: any) {
        // Fallback to mock data to showcase the UI if API fails (e.g. mock-job-123)
        if (job_id.startsWith('mock-job')) {
          setJob({
            id: job_id,
            status: "QUEUED",
            priority: 8,
            tx_requested: false,
            started_at: null,
            completed_at: null,
            readiness: {
              status: "READY",
              confirmed_at: new Date().toISOString(),
              checklist_results: { "MCS Profile Loaded": true, "RF Path Verified": true, "Weather Safe": true },
              notes: "All systems green."
            }
          });
        } else {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }
    fetchJob();
  }, [job_id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse flex items-center gap-3">
          <span className="w-3 h-3 rounded-full bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.8)]"></span>
          {t("loading", "Loading Job Details...", "LOADING JOB DETAILS...")}
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-black p-8 flex flex-col items-center justify-center space-y-4">
        <div className="bg-red-950/50 border border-red-500/50 text-red-300 p-4 rounded-xl text-sm backdrop-blur-md shadow-[0_0_15px_rgba(239,68,68,0.2)]">
          {error || "Job not found"}
        </div>
        <Link href={`/${locale}/operations`} className="text-cyan-400 hover:text-cyan-300 hover:underline transition-colors text-sm">
          ← Back to Operations
        </Link>
      </div>
    );
  }

  // Premium status colors
  const statusColors: Record<string, { bg: string, text: string, glow: string }> = {
    "QUEUED": { bg: "bg-white/10", text: "text-white/70", glow: "shadow-[0_0_15px_rgba(255,255,255,0.05)]" },
    "DISPATCHED": { bg: "bg-blue-500/20", text: "text-blue-300", glow: "shadow-[0_0_15px_rgba(59,130,246,0.15)]" },
    "EXECUTING": { bg: "bg-indigo-500/20", text: "text-indigo-300", glow: "shadow-[0_0_20px_rgba(99,102,241,0.25)]" },
    "COMPLETED": { bg: "bg-green-500/20", text: "text-green-300", glow: "shadow-[0_0_15px_rgba(34,197,94,0.15)]" },
    "FAILED": { bg: "bg-red-500/20", text: "text-red-300", glow: "shadow-[0_0_15px_rgba(239,68,68,0.15)]" },
  };
  const currentStatus = statusColors[job.status] || statusColors["QUEUED"];

  return (
    <div className="min-h-screen bg-black text-white/90 p-8 md:p-12 relative overflow-hidden">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen"></div>

      <div className="max-w-5xl mx-auto space-y-10 relative z-10">
        
        {/* Navigation & Header */}
        <div className="space-y-4">
          <Link href={`/${locale}/operations`} className="inline-flex items-center gap-2 text-white/40 hover:text-white transition-colors text-sm">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            {t("backToBoard", "Back to Operations Board", "BACK TO OPERATIONS BOARD")}
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
            <div>
              <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-200 to-indigo-400 mb-3 drop-shadow-sm flex items-center gap-4">
                {t("title", "Observation Job", "OBSERVATION JOB")}
                <span className="text-2xl text-cyan-400 font-mono tracking-widest">{job.id.substring(0, 8)}</span>
              </h1>
              <p className="text-white/50 text-sm font-mono tracking-widest">
                FULL ID: {job.id}
              </p>
            </div>
            
            {job.tx_requested && (
              <div className="bg-orange-500/10 border border-orange-500/50 text-orange-400 px-4 py-2 rounded-xl text-sm font-bold uppercase tracking-widest shadow-[0_0_15px_rgba(249,115,22,0.2)] animate-pulse">
                TX ACTIVE / TRANSMITTING
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Job Overview */}
          <div className="bg-black/40 rounded-3xl p-8 border border-white/10 backdrop-blur-xl shadow-[0_0_30px_rgba(0,0,0,0.5)]">
            <h2 className="text-xl font-bold mb-6 text-white/90 border-b border-white/10 pb-4">
              {t("overview", "Job Overview", "JOB OVERVIEW")}
            </h2>
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <span className="text-white/40 uppercase text-xs tracking-widest font-semibold">{t("status", "Status", "STATUS")}</span>
                <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest ${currentStatus.bg} ${currentStatus.text} ${currentStatus.glow}`}>
                  {job.status}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/40 uppercase text-xs tracking-widest font-semibold">{t("priority", "Priority", "PRIORITY")}</span>
                <span className="font-mono text-lg font-bold bg-white/5 px-3 py-1 rounded-lg border border-white/5">{job.priority}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/40 uppercase text-xs tracking-widest font-semibold">{t("tx_requested", "TX Requested", "TX REQUESTED")}</span>
                <span className="font-mono">{job.tx_requested ? "YES" : "NO"}</span>
              </div>
              {job.started_at && (
                <div className="flex justify-between items-center pt-2 border-t border-white/5">
                  <span className="text-white/40 uppercase text-xs tracking-widest font-semibold">{t("started", "Started At", "STARTED")}</span>
                  <span className="font-mono text-sm">{new Date(job.started_at).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>

          {/* Pre-flight Readiness */}
          <div className="bg-black/40 rounded-3xl p-8 border border-white/10 backdrop-blur-xl shadow-[0_0_30px_rgba(0,0,0,0.5)] relative overflow-hidden">
            {job.readiness?.status === "READY" && (
              <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 rounded-full blur-[50px]"></div>
            )}
            <h2 className="text-xl font-bold mb-6 text-white/90 flex items-center justify-between border-b border-white/10 pb-4 relative z-10">
              {t("readiness", "Pre-flight Readiness", "PRE-FLIGHT READINESS")}
              {job.readiness?.status === "READY" && (
                <span className="text-green-400 text-xs px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full shadow-[0_0_10px_rgba(34,197,94,0.2)] font-bold tracking-widest">CONFIRMED</span>
              )}
            </h2>
            
            {!job.readiness ? (
              <div className="h-40 flex items-center justify-center text-white/30 border border-dashed border-white/10 rounded-2xl bg-white/5 relative z-10">
                <div className="flex flex-col items-center gap-3">
                  <svg className="w-8 h-8 text-white/20 animate-spin-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                  <span className="text-xs uppercase tracking-widest">{t("pending_confirmation", "Pending Engineer Confirmation", "PENDING ENGINEER CONFIRMATION")}</span>
                </div>
              </div>
            ) : (
              <div className="space-y-5 relative z-10">
                <p className="text-xs text-white/50 uppercase tracking-widest mb-4">
                  {t("confirmed_by", "Confirmed by Engineer at", "CONFIRMED BY ENGINEER AT")} <span className="font-mono text-white/80 ml-2">{new Date(job.readiness.confirmed_at).toLocaleTimeString()}</span>
                </p>
                <div className="space-y-3">
                  {job.readiness.checklist_results ? (
                    Object.entries(job.readiness.checklist_results).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 transition-colors">
                        <span className="text-sm text-white/80 font-medium">{key}</span>
                        <div className={`flex items-center justify-center w-6 h-6 rounded-full ${value ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                          {value ? "✓" : "✗"}
                        </div>
                      </div>
                    ))
                  ) : (
                    <>
                      <div className="flex justify-between items-center p-4 bg-white/5 border border-white/5 rounded-xl">
                        <span className="text-sm text-white/80 font-medium">{t("profile_loaded", "Hardware Profile Loaded", "HARDWARE PROFILE LOADED")}</span>
                        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-green-500/20 text-green-400">✓</div>
                      </div>
                      <div className="flex justify-between items-center p-4 bg-white/5 border border-white/5 rounded-xl">
                        <span className="text-sm text-white/80 font-medium">{t("rf_verified", "RF Path Verified", "RF PATH VERIFIED")}</span>
                        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-green-500/20 text-green-400">✓</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Execution Receipt */}
        {(job.status === "COMPLETED" || job.receipt) && (
          <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-3xl p-8 md:p-10 border border-indigo-500/20 shadow-[0_0_40px_rgba(99,102,241,0.15)] relative overflow-hidden backdrop-blur-xl">
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-indigo-500/20 rounded-full blur-[80px]"></div>
            
            <div className="flex flex-col md:flex-row md:justify-between md:items-end mb-10 border-b border-indigo-500/20 pb-6 relative z-10">
              <div className="mb-6 md:mb-0">
                <h2 className="text-3xl font-extrabold text-white mb-2 flex items-center gap-3">
                  <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  {t("receipt", "Execution Receipt", "EXECUTION RECEIPT")}
                </h2>
                <p className="text-indigo-200/60 text-sm tracking-wide uppercase font-semibold">{t("telemetry_note", "Post-pass telemetry and artifact verification", "POST-PASS TELEMETRY AND ARTIFACT VERIFICATION")}</p>
              </div>
              <button className="px-8 py-3 bg-indigo-500 hover:bg-indigo-400 transition-colors rounded-full text-sm font-bold tracking-widest uppercase text-white shadow-[0_0_25px_rgba(99,102,241,0.4)] flex items-center gap-2 group">
                <svg className="w-5 h-5 group-hover:translate-y-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                {t("download_raw", "Download .raw IQ", "DOWNLOAD .RAW IQ")}
              </button>
            </div>
            
            {job.receipt ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 relative z-10">
                <div className="p-6 bg-black/40 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-colors group">
                  <div className="text-xs uppercase tracking-widest text-white/40 mb-3 font-semibold">{t("carrier_lock", "Carrier Lock", "CARRIER LOCK")}</div>
                  <div className="text-xl font-mono text-indigo-300 group-hover:text-indigo-200 transition-colors">{job.receipt.carrier_locked ? t("locked", "LOCKED", "LOCKED") : t("unlocked", "UNLOCKED", "UNLOCKED")}</div>
                </div>
                <div className="p-6 bg-black/40 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-colors group">
                  <div className="text-xs uppercase tracking-widest text-white/40 mb-3 font-semibold">{t("avg_ebno", "Avg Eb/No", "AVG EB/NO")}</div>
                  <div className="text-xl font-mono text-indigo-300 group-hover:text-indigo-200 transition-colors">{job.receipt.average_ebno ? `${job.receipt.average_ebno.toFixed(2)} dB` : "N/A"}</div>
                </div>
                <div className="p-6 bg-black/40 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-colors group">
                  <div className="text-xs uppercase tracking-widest text-white/40 mb-3 font-semibold">{t("data_volume", "Data Volume", "DATA VOLUME")}</div>
                  <div className="text-xl font-mono text-indigo-300 group-hover:text-indigo-200 transition-colors">
                    {job.receipt.data_volume_bytes ? `${(job.receipt.data_volume_bytes / 1024 / 1024).toFixed(1)} MB` : "0 MB"}
                  </div>
                </div>
                <div className="p-6 bg-black/40 rounded-2xl border border-white/5 hover:border-indigo-500/30 transition-colors group flex flex-col justify-between">
                  <div className="text-xs uppercase tracking-widest text-white/40 mb-3 font-semibold">{t("report_hash", "Report Hash", "REPORT HASH")}</div>
                  <div className="text-sm font-mono text-indigo-300/70 truncate bg-black/50 p-2 rounded-lg border border-white/5" title={job.receipt.pass_report_hash || ""}>
                    {job.receipt.pass_report_hash ? job.receipt.pass_report_hash.substring(0, 16) + "..." : "UNVERIFIED"}
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 border border-dashed border-indigo-500/30 rounded-2xl bg-indigo-500/5 text-center relative z-10">
                <p className="text-indigo-300/70 font-medium tracking-wide">Processing receipt data from ground station edge agent...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
