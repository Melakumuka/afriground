"use client";

import { useState } from "react";
import { useT } from "@/lib/useT";

/* ── Pricing tiers (mirroring backend PRICING dict) ─────────────────── */
const PRICING_TIERS = [
  { id: "standard", label: "Standard", perMin: 15.0, setup: 500 },
  { id: "premium", label: "Premium", perMin: 12.0, setup: 0 },
  { id: "enterprise", label: "Enterprise", perMin: 8.0, setup: 0 },
];

type LineItem = {
  description: string;
  duration_minutes: number;
  rate_per_minute: number;
  subtotal: number;
};

type QuoteResult = {
  id: string;
  total_amount: number;
  status: string;
  line_items: LineItem[];
};

export default function CommercialQuotesPage() {
  const { t } = useT("Commercial");

  /* ── Quote parameters ─────────────────────────────────────────── */
  const [tier, setTier] = useState("standard");
  const [passDurationMin, setPassDurationMin] = useState(10);
  const [passCount, setPassCount] = useState(1);
  const [priority, setPriority] = useState(5);

  /* ── Result state ─────────────────────────────────────────────── */
  const [quote, setQuote] = useState<QuoteResult | null>(null);
  const [accepted, setAccepted] = useState(false);
  const [loading, setLoading] = useState(false);

  const selectedTier = PRICING_TIERS.find((p) => p.id === tier)!;

  /* ── Simulate a local quote (no backend call needed for demo) ── */
  const generateQuote = () => {
    setLoading(true);
    setAccepted(false);
    setTimeout(() => {
      const items: LineItem[] = [];
      for (let i = 0; i < passCount; i++) {
        items.push({
          description: `Pass ${i + 1} · Priority ${priority}`,
          duration_minutes: passDurationMin,
          rate_per_minute: selectedTier.perMin,
          subtotal: passDurationMin * selectedTier.perMin,
        });
      }
      if (selectedTier.setup > 0) {
        items.push({
          description: "One-time setup fee",
          duration_minutes: 0,
          rate_per_minute: 0,
          subtotal: selectedTier.setup,
        });
      }
      const total = items.reduce((s, i) => s + i.subtotal, 0);
      setQuote({
        id: crypto.randomUUID(),
        total_amount: total,
        status: "draft",
        line_items: items,
      });
      setLoading(false);
    }, 600);
  };

  const acceptQuote = () => {
    setAccepted(true);
    if (quote) setQuote({ ...quote, status: "accepted" });
  };

  return (
    <main className="min-h-screen bg-black/95 text-white/90 p-8 md:p-16">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* ── Header ──────────────────────────────────────────── */}
        <div>
          <span className="text-xs font-mono uppercase tracking-[0.25em] text-indigo-400/80 mb-3 block">
            COMMERCIAL ENGINE
          </span>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-500">
            {t("quote_title", "获取报价", "Get a Quote")}
          </h1>
          <p className="mt-3 text-white/50 max-w-xl">
            {t("quote_desc", "配置您的卫星通信需求，获取即时报价。", "Configure your pass requirements and receive an instant price quote.")}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* ── LEFT: Parameters ───────────────────────────────── */}
          <div className="lg:col-span-2 space-y-6">
            {/* Pricing Tier */}
            <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
              <label className="text-xs uppercase tracking-wider text-white/50 block mb-4">Pricing Tier</label>
              <div className="space-y-2">
                {PRICING_TIERS.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setTier(p.id)}
                    className={`w-full text-left p-4 rounded-xl border transition-all ${
                      tier === p.id
                        ? "border-indigo-500 bg-indigo-500/10 shadow-[0_0_20px_rgba(99,102,241,0.15)]"
                        : "border-white/10 bg-black/30 hover:border-white/20"
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">{p.label}</span>
                      <span className="font-mono text-indigo-400">${p.perMin}/min</span>
                    </div>
                    {p.setup > 0 && (
                      <span className="text-xs text-white/40 mt-1 block">+ ${p.setup} setup fee</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Pass Config */}
            <div className="bg-white/5 rounded-2xl p-6 border border-white/10 space-y-5">
              <label className="text-xs uppercase tracking-wider text-white/50 block">Pass Configuration</label>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-white/60">Duration per pass</span>
                  <span className="font-mono text-indigo-400">{passDurationMin} min</span>
                </div>
                <input
                  type="range" min={3} max={20} value={passDurationMin}
                  onChange={(e) => setPassDurationMin(Number(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-white/60">Number of passes</span>
                  <span className="font-mono text-indigo-400">{passCount}</span>
                </div>
                <input
                  type="range" min={1} max={10} value={passCount}
                  onChange={(e) => setPassCount(Number(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-white/60">Priority Level</span>
                  <span className="font-mono text-indigo-400">{priority}</span>
                </div>
                <input
                  type="range" min={1} max={10} value={priority}
                  onChange={(e) => setPriority(Number(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>
            </div>

            <button
              onClick={generateQuote}
              disabled={loading}
              className="w-full py-3 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-xl font-semibold text-white transition-all shadow-[0_0_30px_rgba(99,102,241,0.25)] disabled:opacity-50"
            >
              {loading ? "Calculating..." : t("generate", "生成报价", "Generate Quote")}
            </button>
          </div>

          {/* ── RIGHT: Quote Result ────────────────────────────── */}
          <div className="lg:col-span-3">
            {!quote ? (
              <div className="bg-white/5 rounded-2xl p-12 border border-dashed border-white/10 flex flex-col items-center justify-center h-full text-center">
                <div className="text-6xl mb-6 opacity-30">📋</div>
                <p className="text-white/40 text-lg">{t("no_quote", "还没有报价", "No quote generated yet")}</p>
                <p className="text-white/25 text-sm mt-2">Configure your passes and click Generate</p>
              </div>
            ) : (
              <div className="bg-gradient-to-br from-indigo-500/5 to-purple-500/5 rounded-2xl border border-indigo-500/20 overflow-hidden">
                {/* Quote Header */}
                <div className="p-6 border-b border-white/10 flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-bold">Quote</h3>
                    <p className="text-xs font-mono text-white/40 mt-1">{quote.id}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    quote.status === "accepted"
                      ? "bg-green-500/20 text-green-400"
                      : "bg-yellow-500/20 text-yellow-400"
                  }`}>
                    {quote.status.toUpperCase()}
                  </span>
                </div>

                {/* Line Items */}
                <div className="divide-y divide-white/5">
                  {quote.line_items.map((item, i) => (
                    <div key={i} className="px-6 py-4 flex justify-between items-center">
                      <div>
                        <span className="text-white/80 text-sm">{item.description}</span>
                        {item.duration_minutes > 0 && (
                          <span className="text-white/40 text-xs block mt-1">
                            {item.duration_minutes} min × ${item.rate_per_minute.toFixed(2)}/min
                          </span>
                        )}
                      </div>
                      <span className="font-mono text-indigo-400">${item.subtotal.toFixed(2)}</span>
                    </div>
                  ))}
                </div>

                {/* Total */}
                <div className="px-6 py-5 border-t border-white/10 bg-black/20 flex justify-between items-center">
                  <span className="text-lg font-bold">Total</span>
                  <span className="text-2xl font-bold font-mono text-indigo-400">
                    ${quote.total_amount.toFixed(2)}
                  </span>
                </div>

                {/* Accept */}
                {!accepted && (
                  <div className="p-6 border-t border-white/10">
                    <button
                      onClick={acceptQuote}
                      className="w-full py-3 px-6 bg-green-600 hover:bg-green-500 rounded-xl font-semibold text-white transition-all shadow-[0_0_20px_rgba(34,197,94,0.2)]"
                    >
                      {t("accept", "接受报价", "Accept Quote")}
                    </button>
                  </div>
                )}

                {accepted && (
                  <div className="p-6 border-t border-white/10 bg-green-500/5 text-center">
                    <p className="text-green-400 font-semibold">✅ Quote Accepted — Bookings Reserved</p>
                    <p className="text-green-400/60 text-sm mt-1">Your passes have been locked in.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
