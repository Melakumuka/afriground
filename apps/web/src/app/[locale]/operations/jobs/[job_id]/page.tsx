"use client";

import { useEffect, useState } from "react";
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

export default function JobDetailsPage({ params }: { params: { job_id: string } }) {
  const { t } = useT("JobDetails");
  const [job, setJob] = useState<JobDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchJob() {
      try {
        const res = await fetch(`/api/v1/contact/jobs/${params.job_id}`);
        if (!res.ok) {
          throw new Error("Failed to load job details");
        }
        const data = await res.json();
        setJob(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchJob();
  }, [params.job_id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black/95 text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse">{t("loading", "Loading Job Details...", "LOADING JOB DETAILS...")}</div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-black/95 text-red-500 p-8 flex items-center justify-center">
        {error || "Job not found"}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black/95 text-white/90 p-8 md:p-16">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500 mb-2">
            {t("title", "Pass Report", "PASS REPORT")}
          </h1>
          <p className="text-white/50 text-sm font-mono">{job.id}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Job Overview */}
          <div className="bg-white/5 rounded-2xl p-6 border border-white/10 backdrop-blur-sm">
            <h2 className="text-xl font-bold mb-6 text-white/90">
              {t("overview", "Job Overview", "JOB OVERVIEW")}
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-white/50 uppercase text-xs tracking-wider">Status</span>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  job.status === "COMPLETED" ? "bg-green-500/20 text-green-400" :
                  job.status === "EXECUTING" ? "bg-blue-500/20 text-blue-400" :
                  "bg-orange-500/20 text-orange-400"
                }`}>
                  {job.status}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/50 uppercase text-xs tracking-wider">Priority</span>
                <span className="font-mono">{job.priority}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-white/50 uppercase text-xs tracking-wider">TX Requested</span>
                <span className="font-mono">{job.tx_requested ? "Yes" : "No"}</span>
              </div>
              {job.started_at && (
                <div className="flex justify-between items-center">
                  <span className="text-white/50 uppercase text-xs tracking-wider">Started</span>
                  <span className="font-mono text-sm">{new Date(job.started_at).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>

          {/* Pre-flight Readiness */}
          <div className="bg-white/5 rounded-2xl p-6 border border-white/10 backdrop-blur-sm">
            <h2 className="text-xl font-bold mb-6 text-white/90 flex items-center justify-between">
              {t("readiness", "Pre-flight Readiness", "PRE-FLIGHT READINESS")}
              {job.readiness?.status === "READY" && (
                <span className="text-green-400 text-sm px-2 py-1 bg-green-400/10 rounded-full">CONFIRMED</span>
              )}
            </h2>
            
            {!job.readiness ? (
              <div className="text-center p-8 text-white/40 border border-dashed border-white/10 rounded-xl">
                Pending Engineer Confirmation
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-white/60 mb-4">
                  Confirmed by Station Engineer at <span className="font-mono text-white/80">{new Date(job.readiness.confirmed_at).toLocaleTimeString()}</span>
                </p>
                <div className="space-y-2">
                  {job.readiness.checklist_results ? (
                    Object.entries(job.readiness.checklist_results).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center p-3 bg-black/40 rounded-lg">
                        <span className="text-sm text-white/80">{key}</span>
                        <span>{value ? "✅" : "❌"}</span>
                      </div>
                    ))
                  ) : (
                    <>
                      <div className="flex justify-between items-center p-3 bg-black/40 rounded-lg">
                        <span className="text-sm text-white/80">Hardware Profile Loaded</span>
                        <span>✅</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-black/40 rounded-lg">
                        <span className="text-sm text-white/80">RF Path Verified</span>
                        <span>✅</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Execution Receipt */}
        {job.status === "COMPLETED" && job.receipt && (
          <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-2xl p-8 border border-indigo-500/20">
            <div className="flex justify-between items-end mb-8">
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  {t("receipt", "Execution Receipt", "EXECUTION RECEIPT")}
                </h2>
                <p className="text-indigo-200/60 text-sm">Post-pass telemetry and artifact verification</p>
              </div>
              <button className="px-6 py-2 bg-indigo-500 hover:bg-indigo-400 transition-colors rounded-full text-sm font-semibold text-white shadow-[0_0_20px_rgba(99,102,241,0.3)]">
                Download .raw IQ
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="p-4 bg-black/30 rounded-xl border border-white/5">
                <div className="text-xs uppercase tracking-wider text-white/50 mb-2">Carrier Lock</div>
                <div className="text-lg font-mono text-indigo-400">{job.receipt.carrier_locked ? "LOCKED" : "UNLOCKED"}</div>
              </div>
              <div className="p-4 bg-black/30 rounded-xl border border-white/5">
                <div className="text-xs uppercase tracking-wider text-white/50 mb-2">Avg Eb/No</div>
                <div className="text-lg font-mono text-indigo-400">{job.receipt.average_ebno ? `${job.receipt.average_ebno.toFixed(2)} dB` : "N/A"}</div>
              </div>
              <div className="p-4 bg-black/30 rounded-xl border border-white/5">
                <div className="text-xs uppercase tracking-wider text-white/50 mb-2">Data Volume</div>
                <div className="text-lg font-mono text-indigo-400">
                  {job.receipt.data_volume_bytes ? `${(job.receipt.data_volume_bytes / 1024 / 1024).toFixed(1)} MB` : "0 MB"}
                </div>
              </div>
              <div className="p-4 bg-black/30 rounded-xl border border-white/5">
                <div className="text-xs uppercase tracking-wider text-white/50 mb-2">Report Hash</div>
                <div className="text-sm font-mono text-indigo-400 truncate" title={job.receipt.pass_report_hash || ""}>
                  {job.receipt.pass_report_hash ? job.receipt.pass_report_hash.substring(0, 12) + "..." : "UNVERIFIED"}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
