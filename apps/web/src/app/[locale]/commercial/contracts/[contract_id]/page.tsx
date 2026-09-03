"use client";

import { useState, useEffect } from "react";
import { useT } from "@/lib/useT";

type ContractData = {
  id: string;
  org_name: string;
  start_date: string;
  end_date: string;
  reserved_capacity_minutes: number;
  sla_availability_target: number;
  status: string;
  used_minutes: number;
  remaining_minutes: number;
  pricing_tier: string;
};

/* ── Mock contract data (mirrors backend ContractResponse) ──────── */
const MOCK_CONTRACT: ContractData = {
  id: "00000000-0000-0000-0000-000000000001",
  org_name: "SpaceBridge Inc.",
  start_date: "2026-01-01T00:00:00Z",
  end_date: "2026-12-31T23:59:59Z",
  reserved_capacity_minutes: 12000,
  sla_availability_target: 99.5,
  status: "active",
  used_minutes: 4320,
  remaining_minutes: 7680,
  pricing_tier: "enterprise",
};

function ProgressRing({ value, max, label, color }: { value: number; max: number; label: string; color: string }) {
  const pct = Math.min(100, (value / max) * 100);
  const r = 60;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" className="-rotate-90">
        <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
        <circle
          cx="70" cy="70" r={r} fill="none"
          stroke={color} strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000"
        />
      </svg>
      <div className="absolute mt-10 text-center">
        <div className="text-2xl font-bold font-mono">{pct.toFixed(1)}%</div>
        <div className="text-[10px] uppercase tracking-wider text-white/40">{label}</div>
      </div>
    </div>
  );
}

export default function ContractDashboard({ params }: { params: { contract_id: string } }) {
  const { t } = useT("Commercial");
  const [contract, setContract] = useState<ContractData | null>(null);
  const [daysRemaining, setDaysRemaining] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app: fetch(`/api/v1/commercial/contracts/${params.contract_id}`)
    setTimeout(() => {
      const loaded = { ...MOCK_CONTRACT, id: params.contract_id };
      setContract(loaded);
      const remaining = Math.max(0, Math.ceil(
        (new Date(loaded.end_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
      ));
      setDaysRemaining(remaining);
      setLoading(false);
    }, 400);
  }, [params.contract_id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black/95 text-white/80 p-8 flex items-center justify-center">
        <div className="animate-pulse">{t("loading_contract", "正在加载合同...", "Loading Contract...")}</div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="min-h-screen bg-black/95 text-red-500 p-8 flex items-center justify-center">
        {t("not_found", "未找到合同", "Contract not found")}
      </div>
    );
  }

  const usagePct = (contract.used_minutes / contract.reserved_capacity_minutes) * 100;

  return (
    <main className="min-h-screen bg-black/95 text-white/90 p-8 md:p-16">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* ── Header ────────────────────────────────────────── */}
        <div>
          <span className="text-xs font-mono uppercase tracking-[0.25em] text-emerald-400/80 mb-3 block">
            ENTERPRISE CONTRACT
          </span>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-500">
            {contract.org_name}
          </h1>
          <p className="mt-3 text-white/50 text-sm font-mono">{contract.id}</p>
        </div>

        {/* ── Status Row ────────────────────────────────────── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/5 rounded-xl p-5 border border-white/10">
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">{t("status", "状态", "Status")}</div>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-500/20 text-green-400">
              {contract.status.toUpperCase()}
            </span>
          </div>
          <div className="bg-white/5 rounded-xl p-5 border border-white/10">
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">{t("pricing_tier", "定价档位", "Pricing Tier")}</div>
            <div className="text-lg font-bold text-emerald-400 capitalize">{contract.pricing_tier}</div>
          </div>
          <div className="bg-white/5 rounded-xl p-5 border border-white/10">
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">{t("sla_target", "SLA 目标", "SLA Target")}</div>
            <div className="text-lg font-bold font-mono">{contract.sla_availability_target}%</div>
          </div>
          <div className="bg-white/5 rounded-xl p-5 border border-white/10">
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">{t("days_remaining", "剩余天数", "Days Remaining")}</div>
            <div className="text-lg font-bold font-mono text-emerald-400">{daysRemaining}</div>
          </div>
        </div>

        {/* ── Usage Dashboard ───────────────────────────────── */}
        <div className="bg-gradient-to-br from-emerald-500/5 to-teal-500/5 rounded-2xl border border-emerald-500/20 p-8">
          <h2 className="text-xl font-bold mb-8">{t("usage", "容量使用情况", "Capacity Usage")}</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Usage Bar */}
            <div className="md:col-span-2 space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-white/60">{t("used_capacity", "已用容量", "Used Capacity")}</span>
                  <span className="font-mono text-emerald-400">
                    {contract.used_minutes.toLocaleString()} / {contract.reserved_capacity_minutes.toLocaleString()} min
                  </span>
                </div>
                <div className="h-4 bg-black/40 rounded-full overflow-hidden border border-white/5">
                  <div
                    className={`h-full rounded-full transition-all duration-1000 ${
                      usagePct > 85 ? "bg-gradient-to-r from-red-500 to-orange-500" :
                      usagePct > 60 ? "bg-gradient-to-r from-yellow-500 to-orange-400" :
                      "bg-gradient-to-r from-emerald-500 to-teal-400"
                    }`}
                    style={{ width: `${usagePct}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-white/30 mt-1">
                  <span>0%</span>
                  <span>{usagePct.toFixed(1)}% {t("consumed", "已消耗", "consumed")}</span>
                  <span>100%</span>
                </div>
              </div>

              {/* Metric Cards */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-black/30 rounded-xl border border-white/5 text-center">
                  <div className="text-2xl font-bold font-mono text-emerald-400">
                    {(contract.used_minutes / 60).toFixed(0)}h
                  </div>
                  <div className="text-xs text-white/40 mt-1">{t("used", "已用", "Used")}</div>
                </div>
                <div className="p-4 bg-black/30 rounded-xl border border-white/5 text-center">
                  <div className="text-2xl font-bold font-mono text-teal-400">
                    {(contract.remaining_minutes / 60).toFixed(0)}h
                  </div>
                  <div className="text-xs text-white/40 mt-1">{t("remaining", "剩余", "Remaining")}</div>
                </div>
                <div className="p-4 bg-black/30 rounded-xl border border-white/5 text-center">
                  <div className="text-2xl font-bold font-mono text-white/80">
                    {(contract.reserved_capacity_minutes / 60).toFixed(0)}h
                  </div>
                  <div className="text-xs text-white/40 mt-1">{t("total", "总计", "Total")}</div>
                </div>
              </div>
            </div>

            {/* Progress Ring */}
            <div className="flex items-center justify-center relative">
              <ProgressRing
                value={contract.used_minutes}
                max={contract.reserved_capacity_minutes}
                label={t("consumed", "已消耗", "consumed")}
                color={usagePct > 85 ? "#ef4444" : usagePct > 60 ? "#eab308" : "#10b981"}
              />
            </div>
          </div>
        </div>

        {/* ── Contract Period ───────────────────────────────── */}
        <div className="bg-white/5 rounded-2xl p-8 border border-white/10">
          <h2 className="text-xl font-bold mb-6">{t("period", "合同期", "Contract Period")}</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="text-xs uppercase tracking-wider text-white/40 mb-2">{t("start_date", "开始日期", "Start Date")}</div>
              <div className="font-mono text-white/80">{new Date(contract.start_date).toLocaleDateString()}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider text-white/40 mb-2">{t("end_date", "结束日期", "End Date")}</div>
              <div className="font-mono text-white/80">{new Date(contract.end_date).toLocaleDateString()}</div>
            </div>
          </div>
          {/* Timeline bar */}
          <div className="mt-6">
            <div className="h-2 bg-black/40 rounded-full overflow-hidden border border-white/5">
              <div
                className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-1000"
                style={{ width: `${Math.max(0, 100 - (daysRemaining / 365) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
