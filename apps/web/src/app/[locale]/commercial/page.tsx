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
        
        if (contractsJson.ok) setContracts(contractsJson.data || []);
        if (violationsJson.ok) setViolations(violationsJson.data || []);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-graphite text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse">{t("loading", "Loading Commercial Dashboard...", "LOADING COMMERCIAL DASHBOARD...")}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-graphite text-white/90 p-8">
      <div className="max-w-6xl mx-auto space-y-12">
        <div className="flex justify-between items-end border-b border-white/10 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">
              {t("title", "Commercial & SLA Dashboard", "COMMERCIAL & SLA DASHBOARD")}
            </h1>
            <p className="text-white/50 text-sm font-mono">
              {t("subtitle", "Manage your enterprise GSaaS contracts and monitor SLA performance", "Manage your enterprise GSaaS contracts and monitor SLA performance")}
            </p>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Contracts Section */}
          <div className="space-y-6">
            <h2 className="text-xl font-bold border-b border-white/10 pb-2 flex justify-between items-center">
              <span>{t("contracts_title", "Active Contracts", "Active Contracts")}</span>
              <span className="text-sm font-mono text-white/50 bg-white/5 px-2 py-0.5 rounded-full">{contracts.length}</span>
            </h2>
            
            {contracts.length === 0 ? (
              <div className="border border-dashed border-white/10 rounded-xl p-8 text-center text-white/40 text-sm">
                {t("no_contracts", "No active contracts found.", "No active contracts found.")}
              </div>
            ) : (
              <div className="space-y-4">
                {contracts.map(contract => (
                  <Link 
                    href={`/${locale}/commercial/contracts/${contract.id}`} 
                    key={contract.id}
                    className="block bg-white/5 border border-white/10 rounded-xl p-5 hover:border-signal/50 transition-colors"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="font-mono text-sm text-signal truncate w-48">{contract.id}</h3>
                      <span className={`px-2 py-1 text-[10px] font-bold uppercase rounded ${
                        contract.status === "ACTIVE" ? "bg-green-500/20 text-green-400" : "bg-white/10 text-white/50"
                      }`}>
                        {contract.status}
                      </span>
                    </div>
                    
                    <div className="flex justify-between items-center text-sm mb-4">
                      <span className="text-white/50">Service Tier</span>
                      <span className="font-semibold uppercase tracking-wider">{contract.service_tier}</span>
                    </div>
                    
                    <div className="flex justify-between items-center text-xs text-white/40">
                      <span>{new Date(contract.start_date).toLocaleDateString()}</span>
                      <span>→</span>
                      <span>{new Date(contract.end_date).toLocaleDateString()}</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* SLA Violations Section */}
          <div className="space-y-6">
            <h2 className="text-xl font-bold border-b border-white/10 pb-2 flex justify-between items-center text-orange-400">
              <span>{t("sla_title", "SLA Violations", "SLA Violations")}</span>
              {violations.length > 0 && (
                <span className="text-sm font-mono bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full">
                  {violations.length} Alerts
                </span>
              )}
            </h2>
            
            {violations.length === 0 ? (
              <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-8 text-center text-green-400/80 text-sm flex flex-col items-center gap-2">
                <span className="text-2xl">✓</span>
                {t("no_violations", "All SLA targets are currently being met.", "All SLA targets are currently being met.")}
              </div>
            ) : (
              <div className="space-y-4">
                {violations.map(v => (
                  <div key={v.id} className="bg-orange-500/5 border border-orange-500/20 rounded-xl p-5">
                    <div className="flex justify-between items-start mb-3">
                      <span className="text-xs font-bold uppercase tracking-wider text-orange-400 bg-orange-500/10 px-2 py-1 rounded">
                        {v.sla_type.replace(/_/g, ' ')}
                      </span>
                      <span className="text-[10px] font-mono text-white/40">
                        {new Date(v.violated_at).toLocaleDateString()}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mt-4 text-sm bg-black/20 p-3 rounded-lg">
                      <div>
                        <div className="text-white/40 text-[10px] uppercase mb-1">Target</div>
                        <div className="font-mono text-green-400">{v.target_value} {v.unit}</div>
                      </div>
                      <div>
                        <div className="text-white/40 text-[10px] uppercase mb-1">Actual</div>
                        <div className="font-mono text-red-400">{v.actual_value} {v.unit}</div>
                      </div>
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
