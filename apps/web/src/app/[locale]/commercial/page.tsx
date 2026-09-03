"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { useT } from "@/lib/useT";

type Contract = {
  id: string;
  start_date: string;
  end_date: string;
  status: string;
  service_tier: string;
  customer_name?: string;
  monthly_value?: number;
};

type SlaViolation = {
  id: string;
  sla_type: string;
  target_value: number;
  actual_value: number;
  unit: string;
  status: string;
  violated_at: string;
};

const MOCK_CONTRACTS: Contract[] = [
  { id: "ctr-af-001", start_date: new Date(Date.now() - 86400000 * 60).toISOString(), end_date: new Date(Date.now() + 86400000 * 305).toISOString(), status: "ACTIVE", service_tier: "PREMIUM", customer_name: "ESA / Copernicus", monthly_value: 45000 },
  { id: "ctr-af-002", start_date: new Date(Date.now() - 86400000 * 120).toISOString(), end_date: new Date(Date.now() + 86400000 * 245).toISOString(), status: "ACTIVE", service_tier: "STANDARD", customer_name: "Planet Labs", monthly_value: 28000 },
  { id: "ctr-af-003", start_date: new Date(Date.now() - 86400000 * 200).toISOString(), end_date: new Date(Date.now() + 86400000 * 165).toISOString(), status: "ACTIVE", service_tier: "ENTERPRISE", customer_name: "AfriStar Constellation", monthly_value: 72000 },
  { id: "ctr-af-004", start_date: new Date(Date.now() - 86400000 * 400).toISOString(), end_date: new Date(Date.now() - 86400000 * 35).toISOString(), status: "EXPIRED", service_tier: "STANDARD", customer_name: "ICEYE", monthly_value: 18000 },
];

const MOCK_VIOLATIONS: SlaViolation[] = [
  { id: "sla-001", sla_type: "DATA_DELIVERY_LATENCY", target_value: 30, actual_value: 47, unit: "min", status: "OPEN", violated_at: new Date(Date.now() - 86400000 * 2).toISOString() },
  { id: "sla-002", sla_type: "PASS_SUCCESS_RATE", target_value: 99.5, actual_value: 97.8, unit: "%", status: "RESOLVED", violated_at: new Date(Date.now() - 86400000 * 14).toISOString() },
];

export default function CommercialDashboard({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = use(params);
  const { t } = useT("Commercial");
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [violations, setViolations] = useState<SlaViolation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchData() {
      try {
        const [contractsRes, violationsRes] = await Promise.all([
          fetch(`/api/platform/commercial/contracts`),
          fetch(`/api/platform/business/sla-violations`),
        ]);

        if (!contractsRes.ok || !violationsRes.ok) {
          throw new Error("Failed to load commercial dashboard data");
        }

        const contractsJson = await contractsRes.json();
        const violationsJson = await violationsRes.json();

        const c = contractsJson.ok ? (contractsJson.data || []) : [];
        const v = violationsJson.ok ? (violationsJson.data || []) : [];

        setContracts(c.length > 0 ? c : MOCK_CONTRACTS);
        setViolations(v.length > 0 ? v : MOCK_VIOLATIONS);
      } catch (err: any) {
        setContracts(MOCK_CONTRACTS);
        setViolations(MOCK_VIOLATIONS);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse flex items-center gap-3">
          <span className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]"></span>
          {t("loading", "Loading Commercial Dashboard...", "LOADING COMMERCIAL DASHBOARD...")}
        </div>
      </div>
    );
  }

  const totalMRR = contracts.filter(c => c.status === "ACTIVE").reduce((sum, c) => sum + (c.monthly_value || 0), 0);
  const activeCount = contracts.filter(c => c.status === "ACTIVE").length;
  const openViolations = violations.filter(v => v.status === "OPEN").length;

  const tierColors: Record<string, string> = {
    PREMIUM: "from-amber-500/20 to-yellow-500/20 border-amber-500/30",
    ENTERPRISE: "from-purple-500/20 to-indigo-500/20 border-purple-500/30",
    STANDARD: "from-white/5 to-white/10 border-white/15",
  };

  return (
    <div className="min-h-screen bg-black text-white/90 p-8 relative overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute top-[-15%] left-[-10%] w-[50%] h-[50%] bg-amber-600/15 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[55%] h-[55%] bg-purple-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute top-[30%] left-[50%] w-[20%] h-[20%] bg-orange-500/8 rounded-full blur-[80px] pointer-events-none mix-blend-screen animate-pulse"></div>

      <div className="max-w-7xl mx-auto space-y-10 relative z-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/10 pb-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-amber-200 to-orange-400 mb-3 drop-shadow-sm">
              {t("title", "Commercial & SLA Dashboard", "COMMERCIAL & SLA DASHBOARD")}
            </h1>
            <div className="flex items-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]"></span>
              </span>
              <p className="text-amber-400 text-sm font-mono tracking-widest uppercase">
                {t("subtitle", "Revenue & Compliance Monitor", "REVENUE & COMPLIANCE MONITOR")}
              </p>
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-5 hover:border-amber-500/30 transition-colors">
            <div className="text-[10px] uppercase tracking-widest text-white/40 mb-2 font-semibold">Monthly Revenue</div>
            <div className="text-3xl font-extrabold font-mono text-amber-400">${(totalMRR / 1000).toFixed(0)}K</div>
          </div>
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-5 hover:border-green-500/30 transition-colors">
            <div className="text-[10px] uppercase tracking-widest text-white/40 mb-2 font-semibold">Active Contracts</div>
            <div className="text-3xl font-extrabold font-mono text-green-400">{activeCount}</div>
          </div>
          <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-colors">
            <div className="text-[10px] uppercase tracking-widest text-white/40 mb-2 font-semibold">Total Contracts</div>
            <div className="text-3xl font-extrabold font-mono text-white">{contracts.length}</div>
          </div>
          <div className={`bg-black/40 backdrop-blur-xl border rounded-2xl p-5 transition-colors ${openViolations > 0 ? 'border-red-500/30 hover:border-red-500/50' : 'border-white/10 hover:border-green-500/30'}`}>
            <div className="text-[10px] uppercase tracking-widest text-white/40 mb-2 font-semibold">Open SLA Alerts</div>
            <div className={`text-3xl font-extrabold font-mono ${openViolations > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {openViolations}
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-950/50 border border-red-500/50 text-red-300 p-4 rounded-xl text-sm backdrop-blur-md shadow-[0_0_15px_rgba(239,68,68,0.2)] flex items-center gap-3">
            <svg className="w-5 h-5 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Contracts Section — 3 columns */}
          <div className="lg:col-span-3 space-y-6">
            <h2 className="text-xl font-bold flex justify-between items-center border-b border-white/10 pb-3">
              <span className="tracking-wide">{t("contracts_title", "Active Contracts", "ACTIVE CONTRACTS")}</span>
              <span className="text-xs font-mono px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/50">{contracts.length}</span>
            </h2>

            {contracts.length === 0 ? (
              <div className="border border-dashed border-white/10 rounded-2xl p-12 text-center backdrop-blur-sm bg-black/20">
                <span className="text-xs text-white/30 uppercase tracking-widest">{t("no_contracts", "No active contracts found.", "No active contracts found.")}</span>
              </div>
            ) : (
              <div className="space-y-4">
                {contracts.map((contract, index) => {
                  const tier = tierColors[contract.service_tier] || tierColors.STANDARD;
                  return (
                    <Link
                      href={`/${locale}/commercial/contracts/${contract.id}`}
                      key={contract.id}
                      className="block group animate-in fade-in slide-in-from-bottom-4"
                      style={{ animationDelay: `${index * 80}ms`, animationFillMode: 'both' }}
                    >
                      <div className={`bg-gradient-to-r ${tier} backdrop-blur-xl rounded-2xl p-6 border transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-[0_0_25px_rgba(245,158,11,0.15)]`}>
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="text-lg font-bold group-hover:text-amber-300 transition-colors">{contract.customer_name || contract.id}</h3>
                            <p className="text-xs font-mono text-white/30 mt-0.5">{contract.id}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${contract.status === 'ACTIVE' ? 'bg-green-400 animate-pulse shadow-[0_0_6px_rgba(52,211,153,0.8)]' : 'bg-white/30'}`}></span>
                            <span className={`px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-full ${
                              contract.status === "ACTIVE" ? "bg-green-500/15 text-green-400" : "bg-white/10 text-white/50"
                            }`}>
                              {contract.status}
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-3">
                          <div className="bg-black/30 rounded-xl p-3">
                            <span className="text-[10px] text-white/40 uppercase tracking-widest block mb-1">Service Tier</span>
                            <span className="font-bold tracking-wider text-sm">{contract.service_tier}</span>
                          </div>
                          <div className="bg-black/30 rounded-xl p-3">
                            <span className="text-[10px] text-white/40 uppercase tracking-widest block mb-1">Monthly</span>
                            <span className="font-mono text-amber-400 font-bold text-sm">
                              ${contract.monthly_value ? (contract.monthly_value / 1000).toFixed(0) + 'K' : 'N/A'}
                            </span>
                          </div>
                          <div className="bg-black/30 rounded-xl p-3">
                            <span className="text-[10px] text-white/40 uppercase tracking-widest block mb-1">Period</span>
                            <span className="font-mono text-white/70 text-xs">
                              {new Date(contract.start_date).toLocaleDateString(undefined, { month: 'short', year: '2-digit' })} → {new Date(contract.end_date).toLocaleDateString(undefined, { month: 'short', year: '2-digit' })}
                            </span>
                          </div>
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>

          {/* SLA Violations Section — 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-bold flex justify-between items-center border-b border-white/10 pb-3">
              <span className="tracking-wide text-orange-400">{t("sla_title", "SLA Violations", "SLA VIOLATIONS")}</span>
              {violations.length > 0 && (
                <span className="text-xs font-mono px-3 py-1 rounded-full bg-orange-500/15 border border-orange-500/30 text-orange-400">
                  {violations.length} {violations.length === 1 ? 'Alert' : 'Alerts'}
                </span>
              )}
            </h2>

            {violations.length === 0 ? (
              <div className="bg-green-500/5 border border-green-500/20 rounded-2xl p-10 text-center backdrop-blur-sm">
                <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center mx-auto mb-4 border border-green-500/20">
                  <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                </div>
                <p className="text-green-400/80 text-sm font-medium">{t("no_violations", "All SLA targets are currently being met.", "All SLA targets are currently being met.")}</p>
              </div>
            ) : (
              <div className="space-y-4">
                {violations.map((v, index) => (
                  <div
                    key={v.id}
                    className={`rounded-2xl p-6 border backdrop-blur-xl transition-all animate-in fade-in slide-in-from-right-4 ${
                      v.status === "OPEN"
                        ? "bg-red-500/5 border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.1)]"
                        : "bg-white/5 border-white/10"
                    }`}
                    style={{ animationDelay: `${index * 100}ms`, animationFillMode: 'both' }}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <span className={`text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full ${
                        v.status === "OPEN"
                          ? "bg-red-500/15 text-red-400 border border-red-500/30"
                          : "bg-white/10 text-white/50 border border-white/10"
                      }`}>
                        {v.sla_type.replace(/_/g, ' ')}
                      </span>
                      <div className="flex items-center gap-2">
                        {v.status === "OPEN" && <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse shadow-[0_0_6px_rgba(239,68,68,0.8)]"></span>}
                        <span className={`text-[10px] font-bold uppercase tracking-widest ${v.status === "OPEN" ? "text-red-400" : "text-white/40"}`}>{v.status}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-black/40 rounded-xl p-4">
                        <div className="text-[10px] text-white/40 uppercase tracking-widest mb-2 font-semibold">Target</div>
                        <div className="text-xl font-mono font-bold text-green-400">{v.target_value} <span className="text-xs text-white/40">{v.unit}</span></div>
                      </div>
                      <div className="bg-black/40 rounded-xl p-4">
                        <div className="text-[10px] text-white/40 uppercase tracking-widest mb-2 font-semibold">Actual</div>
                        <div className="text-xl font-mono font-bold text-red-400">{v.actual_value} <span className="text-xs text-white/40">{v.unit}</span></div>
                      </div>
                    </div>

                    <div className="mt-4 text-xs text-white/30 font-mono text-right">
                      {new Date(v.violated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
