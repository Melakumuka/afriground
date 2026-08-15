"use client";

import { useEffect, useRef, useState } from "react";
import { STATIONS } from "@/data/stations";
import { useT } from "@/lib/useT";

type SatSearch = { norad: string; name: string; epochUtc: string };

type SatSearchResponse = { list?: SatSearch[]; error?: string; source?: "live" | "offline" };

type PassInfo = {
  aosIso: string;
  losIso: string;
  durationMin: number;
  maxElevationDeg: number;
  aosAzimuthDeg: number;
};

type PassesResponse = {
  satellite?: SatSearch;
  station?: { id: string; name: string };
  mask?: number;
  catalog?: "live" | "offline";
  passes?: PassInfo[];
  error?: string;
};

type Quote = {
  total: number;
  breakdown: { desc: string; cost: number }[];
};

const RATE_PER_MIN = 15.0;

const SIM_FALLBACK_PASSES: PassInfo[] = [
  { aosIso: "2026-08-14T14:30:00Z", losIso: "2026-08-14T14:40:15Z", durationMin: 10.3, maxElevationDeg: 82.4, aosAzimuthDeg: 154.2 },
  { aosIso: "2026-08-14T16:15:00Z", losIso: "2026-08-14T16:23:45Z", durationMin: 8.8, maxElevationDeg: 45.1, aosAzimuthDeg: 12.7 },
  { aosIso: "2026-08-15T04:20:00Z", losIso: "2026-08-15T04:31:20Z", durationMin: 11.3, maxElevationDeg: 88.9, aosAzimuthDeg: 331.4 },
];

export default function BookingWizard() {
  const { t, isZh, ns } = useT("Booking");
  const zhSteps = ["卫星", "过境", "报价与预订"];
  const enSteps = ["Satellite", "Passes", "Quote & Book"];
  const STEPS: string[] = Array.isArray(ns.steps) ? (ns.steps as string[]) : isZh ? zhSteps : enSteps;
  const [step, setStep] = useState(1);

  // Step 1 · catalog search
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SatSearch[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [sat, setSat] = useState<SatSearch | null>(null);
  const [noradManual, setNoradManual] = useState("");
  const [stationId, setStationId] = useState("entoto");
  const [elevation, setElevation] = useState(5);
  const [days, setDays] = useState(2);

  // Step 2 · prediction
  const [predicting, setPredicting] = useState(false);
  const [predError, setPredError] = useState("");
  const [usingFallback, setUsingFallback] = useState(false);
  const [catalogSource, setCatalogSource] = useState<"live" | "offline" | null>(null);
  const [passes, setPasses] = useState<PassInfo[] | null>(null);
  const [passMeta, setPassMeta] = useState<PassesResponse["satellite"] | null>(null);
  const [selectedPassIndex, setSelectedPassIndex] = useState<number | null>(null);

  // Step 3 · quote
  const [quote, setQuote] = useState<Quote | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const debounceId = useRef(0);

  useEffect(() => () => window.clearTimeout(debounceId.current), []);

  const runSearch = async (q: string): Promise<SatSearch[]> => {
    if (q.trim().length < 2) {
      setResults([]);
      setSearchError("");
      return [];
    }
    setSearching(true);
    try {
      const res = await fetch(`/api/satellites?q=${encodeURIComponent(q.trim())}`);
      const data = (await res.json()) as SatSearchResponse;
      const list = data.list ?? [];
      setResults(list);
      setCatalogSource(data.source ?? null);
      setSearchError(data.error ?? "");
      return list;
    } catch {
      setResults([]);
      setSearchError(t("err_feed", "星历源不可达", "GP FEED UNREACHABLE"));
      return [];
    } finally {
      setSearching(false);
    }
  };

  const handleQueryChange = (v: string) => {
    setQuery(v);
    if (v.trim().length < 2) {
      window.clearTimeout(debounceId.current);
      setResults([]);
      setSearchError("");
      return;
    }
    window.clearTimeout(debounceId.current);
    setSearching(true);
    debounceId.current = window.setTimeout(() => void runSearch(v), 400);
  };

  const handleManualLookup = async () => {
    const n = noradManual.trim();
    if (!/^\d{1,9}$/.test(n)) {
      setSearchError(t("err_norad", "NORAD 编号必须为 1–9 位数字", "NORAD ID MUST BE 1–9 DIGITS"));
      return;
    }
    const list = await runSearch(n);
    const exact = list.find((r) => r.norad === n);
    if (exact) {
      setSat(exact);
      setQuery(exact.name);
      setResults([]);
    }
  };

  const handlePick = (s: SatSearch) => {
    setSat(s);
    setQuery(s.name);
    setResults([]);
    setNoradManual(s.norad);
  };

  const handlePredict = async () => {
    if (!sat) return;
    setPredicting(true);
    setPredError("");
    setUsingFallback(false);
    setPasses(null);
    setPassMeta(null);
    setSelectedPassIndex(null);
    try {
      const res = await fetch(
        `/api/passes?norad=${sat.norad}&stationId=${stationId}&days=${days}&elevation=${elevation}`
      );
      const data = (await res.json()) as PassesResponse;
      if (data.error || !data.passes) {
        setPredError(data.error ?? t("err_engine", "引擎错误", "ENGINE ERROR"));
      } else {
        setPasses(data.passes);
        setPassMeta(data.satellite ?? null);
        setCatalogSource(data.catalog ?? null);
        if (data.passes.length === 0) setPredError(t("err_no_passes", "所选窗口内无过境", "NO PASSES IN SELECTED WINDOW"));
      }
      setStep(2);
    } catch {
      setPredError(t("err_sgp4", "SGP4 引擎不可达", "SGP4 ENGINE UNREACHABLE"));
      setStep(2);
    }
    setPredicting(false);
  };

  const handleUseSimulated = () => {
    setUsingFallback(true);
    setPredError("");
    setPasses(SIM_FALLBACK_PASSES);
  };

  const startQuote = () => {
    if (selectedPassIndex === null || !passes) return;
    const pass = passes[selectedPassIndex];
    setIsChecking(true);
    window.setTimeout(() => {
      const cost = Math.round(pass.durationMin * RATE_PER_MIN * 100) / 100;
      setQuote({
        total: cost,
        breakdown: [
          {
            desc: t("pass_duration_desc", "过境时长（{min} 分钟）", "Pass Duration ({min} min)")
              .replace("{min}", pass.durationMin.toFixed(1)),
            cost,
          },
        ],
      });
      setIsChecking(false);
      setStep(3);
    }, 900);
  };

  const handleConfirm = () => {
    setIsChecking(true);
    window.setTimeout(() => {
      setIsChecking(false);
      setStep(4);
    }, 900);
  };

  const station = STATIONS.find((s) => s.id === stationId);

  return (
    <main className="min-h-screen bg-graphite text-ink">
      {/* ── Ops header ─────────────────────────────────────────── */}
      <div className="border-b border-graphite-600/60">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-14">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("module", "运营模块 01 · 过境调度", "OPS-MODULE 01 · PASS SCHEDULING")}
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                {t("title", "预订卫星过境", "Schedule a Satellite Pass")}
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-xl">
                {t("subtitle", "检索 NORAD 实时活跃星历目录，选择地面站，为您的航天器获取基于 SGP4 传播的过境预报。", "Search the live NORAD active catalog, pick a ground station, and get SGP4-propagated pass predictions for your vehicle.")}
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 border border-green/50">
              <span className="w-1.5 h-1.5 rounded-full bg-green-soft animate-pulse" />
              <span className="mono-label text-green-soft">{t("live_badge", "CelesTrak GP · 实时星历目录", "CelesTrak GP · Live Catalog")}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 sm:px-10 lg:px-14 py-12">
        <div className="console-panel rounded-sm overflow-hidden">
          {/* Stepper */}
          <div className="px-6 sm:px-10 py-6 border-b border-graphite-600/60 bg-graphite-700/40">
            <div className="flex items-center gap-4">
              {STEPS.map((label, i) => (
                <div key={label} className={`flex items-center gap-4 ${i > 0 ? "flex-1" : ""}`}>
                  {i > 0 && (
                    <div className={`flex-1 h-px ${step > i ? "bg-signal/60" : "bg-graphite-600"}`} />
                  )}
                  <div className="flex items-center gap-2.5 shrink-0">
                    <span
                      className={`w-7 h-7 grid place-items-center font-mono text-xs font-bold border ${
                        step > i ? "bg-signal text-graphite border-signal" : "border-graphite-600 text-steel"
                      }`}
                    >
                      {i + 1}
                    </span>
                    <span className={`mono-label hidden sm:block ${step > i ? "text-steel-2" : "text-graphite-mute"}`}>
                      {label}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="px-6 sm:px-10 py-10">
            {/* STEP 1 · SATELLITE + STATION */}
            {step === 1 && (
              <div className="space-y-10">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                  {/* Left: satellite search */}
                  <div className="lg:col-span-7 space-y-5">
                    <span className="mono-label text-signal-soft">{t("identify", "01 · 选择航天器", "01 · IDENTIFY VEHICLE")}</span>

                    <div>
                      <label className="mono-label text-steel-2 block mb-2">{t("search_label", "按名称搜索活跃星历目录", "SEARCH ACTIVE CATALOG BY NAME")}</label>
                      <input
                        type="text"
                        value={query}
                        onChange={(e) => handleQueryChange(e.target.value)}
                        placeholder={t("search_placeholder", "例如 Sentinel、Aqua、ISS、Starlink...", "e.g. Sentinel, Aqua, ISS, Starlink...")}
                        className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
                      />
                    </div>

                    {searching && (
                      <p className="mono-label text-graphite-mute flex items-center gap-3">
                        <span className="signal-indicator" />
                        {t("querying", "正在查询 NORAD 星历目录...", "QUERYING NORAD CATALOG...")}
                      </p>
                    )}

                    {!searching && results.length > 0 && (
                      <div className="border border-graphite-600 max-h-72 overflow-y-auto divide-y divide-graphite-600/40">
                        {catalogSource === "offline" && (
                          <div className="px-4 py-2 bg-signal/10 border-b border-signal/30">
                            <span className="font-mono text-[10px] text-signal-soft uppercase tracking-wider">
                              {t("offline_banner", "离线备用星历目录 · 15 颗卫星", "OFFLINE FALLBACK CATALOG · 15 VEHICLES")}
                            </span>
                          </div>
                        )}
                        {results.map((r) => (
                          <button
                            key={r.norad}
                            onClick={() => handlePick(r)}
                            className="w-full text-left px-4 py-3 flex items-center justify-between gap-4 hover:bg-graphite-700/40 transition-colors"
                          >
                            <span className="text-sm text-white">{r.name}</span>
                            <span className="font-mono text-xs text-signal-soft shrink-0">
                              NORAD {r.norad}
                            </span>
                          </button>
                        ))}
                      </div>
                    )}

                    {!searching && results.length === 0 && query.trim().length >= 2 && !searchError && (
                      <p className="mono-label text-graphite-mute">{t("no_matches", "活跃星历目录中无匹配结果", "NO MATCHES IN ACTIVE CATALOG")}</p>
                    )}

                    {searchError && (
                      <p className="mono-label text-signal-soft">{searchError}</p>
                    )}

                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-px bg-graphite-600" />
                      <span className="mono-label text-graphite-mute">{t("or", "或", "OR")}</span>
                      <div className="flex-1 h-px bg-graphite-600" />
                    </div>

                    <div className="flex gap-3 items-end">
                      <div className="flex-1">
                        <label className="mono-label text-steel-2 block mb-2">{t("norad_label", "NORAD 星历编号", "NORAD CATALOG ID")}</label>
                        <input
                          type="number"
                          value={noradManual}
                          onChange={(e) => setNoradManual(e.target.value)}
                          placeholder={t("norad_placeholder", "例如 25544（国际空间站）", "e.g. 25544 (ISS)")}
                          className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
                        />
                      </div>
                      <button
                        onClick={handleManualLookup}
                        className="px-5 py-3 border border-graphite-600 text-steel-2 hover:text-white hover:border-steel font-semibold transition-colors"
                      >
                        {t("lookup", "查询", "Lookup")}
                      </button>
                    </div>

                    {sat && (
                      <div className="flex flex-wrap items-center gap-3 border border-signal/40 bg-signal/10 px-4 py-3">
                        <span className="font-display font-semibold text-white text-sm">{sat.name}</span>
                        <span className="font-mono text-xs text-signal-soft">NORAD {sat.norad}</span>
                        <span className="font-mono text-[10px] text-graphite-mute">
                          {t("tle_epoch", "TLE 历元 · ", "TLE EPOCH · ")}{sat.epochUtc}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Right: station + config */}
                  <div className="lg:col-span-5 space-y-5">
                    <span className="mono-label text-signal-soft">{t("station_section", "02 · 目标地面站", "02 · TARGET STATION")}</span>

                    <div>
                      <label className="mono-label text-steel-2 block mb-2">{t("station_label", "地面站", "GROUND STATION")}</label>
                      <select
                        value={stationId}
                        onChange={(e) => setStationId(e.target.value)}
                        className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
                      >
                        {STATIONS.map((s) => (
                          <option key={s.id} value={s.id}>
                            {s.name} · {s.country.replace(" 🇪🇹", "").replace(" 🇿🇦", "").replace(" 🇰🇪", "").replace(" 🇳🇬", "").replace(" 🇪🇬", "").replace(" 🇸🇳", "")}
                          </option>
                        ))}
                      </select>
                    </div>

                    {station && (
                      <div className="border border-graphite-600 bg-graphite px-4 py-3 space-y-1.5 font-mono text-xs text-steel-2">
                        <div className="flex justify-between">
                          <span className="text-graphite-mute">{t("position", "坐标", "POSITION")}</span>
                          <span>
                            {Math.abs(station.lat).toFixed(3)}°{station.lat >= 0 ? "N" : "S"} ·{" "}
                            {Math.abs(station.lng).toFixed(3)}°{station.lng < 0 ? "W" : "E"}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-graphite-mute">{t("bands", "频段", "BANDS")}</span>
                          <span>{station.bands.join(" · ")}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-graphite-mute">{t("dish", "天线口径", "DISH")}</span>
                          <span>{station.dishSize}</span>
                        </div>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-5">
                      <div>
                        <label className="mono-label text-steel-2 block mb-2">{t("mask_label", "仰角掩模", "ELEVATION MASK")}</label>
                        <select
                          value={elevation}
                          onChange={(e) => setElevation(Number(e.target.value))}
                          className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
                        >
                          <option value={3}>3.0°</option>
                          <option value={5}>5.0°</option>
                          <option value={10}>10.0°</option>
                          <option value={15}>15.0°</option>
                        </select>
                      </div>
                      <div>
                        <label className="mono-label text-steel-2 block mb-2">{t("window_label", "预报时间窗口", "LOOKAHEAD WINDOW")}</label>
                        <select
                          value={days}
                          onChange={(e) => setDays(Number(e.target.value))}
                          className="w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none"
                        >
                          <option value={1}>{t("h24", "24 小时", "24 hours")}</option>
                          <option value={2}>{t("h48", "48 小时", "48 hours")}</option>
                          <option value={3}>{t("h72", "72 小时", "72 hours")}</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  onClick={handlePredict}
                  disabled={!sat || predicting}
                  className="w-full py-3.5 bg-signal hover:bg-signal-soft text-graphite font-semibold rounded-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {predicting ? t("predicting", "正在传播 SGP4 ...", "Propagating SGP4 ...") : t("predict", "预测过境", "Predict Passes")}
                </button>
              </div>
            )}

            {/* STEP 2 · PASSES */}
            {step === 2 && (
              <div className="space-y-8">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="mono-label text-signal-soft">{t("available", "可用过境", "AVAILABLE PASSES")}</span>
                    {passMeta && (
                      <>
                        <span className="font-mono text-xs text-steel-2">
                          {passMeta.name} · NORAD {passMeta.norad}
                        </span>
                        <span className="font-mono text-[10px] text-graphite-mute">
                          GP {passMeta.epochUtc}
                        </span>
                      </>
                    )}
                  </div>
                  {usingFallback && (
                    <span className="px-2.5 py-1 border border-signal/50 text-signal-soft font-mono text-[10px]">
                      {t("sim_fallback", "模拟回退 · 非实时", "SIM FALLBACK · NOT LIVE")}
                    </span>
                  )}
                  {!usingFallback && catalogSource === "offline" && (
                    <span className="px-2.5 py-1 border border-signal/50 text-signal-soft font-mono text-[10px]">
                      {t("offline_gp", "离线星历 · 备用 TLE", "OFFLINE GP · FALLBACK TLEs")}
                    </span>
                  )}
                </div>

                {predError && (
                  <div className="border border-signal/50 bg-signal/10 px-5 py-4">
                    <p className="mono-label text-signal-soft">{predError}</p>
                    <button
                      onClick={handleUseSimulated}
                      className="mt-3 px-4 py-2 border border-signal/50 text-signal-soft hover:bg-signal/10 font-mono text-xs"
                    >
                      {t("load_sim", "改为载入模拟过境", "LOAD SIMULATED PASSES INSTEAD")}
                    </button>
                  </div>
                )}

                {passes && passes.length > 0 && (
                  <div className="space-y-3">
                    {passes.map((p, i) => (
                      <button
                        key={`${p.aosIso}-${i}`}
                        onClick={() => setSelectedPassIndex(i)}
                        className={`w-full p-5 border text-left transition-colors ${
                          selectedPassIndex === i
                            ? "border-signal/70 bg-signal/10"
                            : "border-graphite-600 hover:border-steel bg-graphite/60"
                        }`}
                      >
                        <div className="flex flex-wrap items-center justify-between gap-4">
                          <div className="flex items-center gap-4">
                            <span className={`w-7 h-7 grid place-items-center font-mono text-xs font-bold border ${selectedPassIndex === i ? "border-signal/70 text-signal-soft" : "border-graphite-600 text-steel"}`}>
                              {String(i + 1).padStart(2, "0")}
                            </span>
                            <div>
                              <div className="font-display font-semibold text-white">
                                {new Date(p.aosIso).toLocaleDateString(isZh ? "zh-CN" : "en-US", { weekday: "short", month: "short", day: "numeric" })}{" "}
                                {new Date(p.aosIso).toLocaleTimeString(isZh ? "zh-CN" : "en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" })} UTC
                              </div>
                              <div className="font-mono text-xs text-graphite-mute mt-0.5">
                                {t("los", "结束", "LOS")} {new Date(p.losIso).toLocaleTimeString(isZh ? "zh-CN" : "en-US", { hour: "2-digit", minute: "2-digit" })} UTC
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-5 font-mono text-sm">
                            <div className="text-right">
                              <div className="text-steel-2">{p.durationMin.toFixed(1)} {t("min", "分钟", "min")}</div>
                              <div className="text-[10px] text-graphite-mute uppercase tracking-wider">{t("duration", "持续时长", "Duration")}</div>
                            </div>
                            <div className="text-right">
                              <div className="text-green-soft">{p.maxElevationDeg.toFixed(1)}°</div>
                              <div className="text-[10px] text-graphite-mute uppercase tracking-wider">{t("max_el", "最大仰角", "Max El")}</div>
                            </div>
                            <div className="text-right hidden sm:block">
                              <div className="text-signal-soft">{p.aosAzimuthDeg.toFixed(0)}°</div>
                              <div className="text-[10px] text-graphite-mute uppercase tracking-wider">{t("aos_az", "捕获方位角", "AOS Az")}</div>
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                <div className="flex gap-3">
                  <button
                    onClick={() => setStep(1)}
                    className="px-6 py-3.5 border border-graphite-600 font-medium text-steel-2 hover:text-white hover:border-steel transition-colors"
                  >
                    {t("back", "返回", "Back")}
                  </button>
                  <button
                    onClick={startQuote}
                    disabled={selectedPassIndex === null}
                    className="flex-1 py-3.5 bg-signal hover:bg-signal-soft text-graphite font-semibold transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {t("review_quote", "查看并申请报价", "Review & Request Quote")}
                  </button>
                </div>
              </div>
            )}

            {/* STEP 3 · QUOTE & BOOK */}
            {step === 3 && quote && selectedPassIndex !== null && passes && (
              <div className="space-y-8">
                <span className="mono-label text-signal-soft">{t("review_quote", "查看并申请报价", "REVIEW & REQUEST QUOTE")}</span>

                <div className="p-6 sm:p-8 border border-graphite-600 bg-graphite">
                  <span className="mono-label text-steel-2">{t("selected_pass", "已选过境", "SELECTED PASS")}</span>
                  <p className="mt-3 font-mono text-xs text-graphite-mute">
                    {passMeta?.name ?? t("vehicle", "航天器", "Vehicle")} · NORAD {passMeta?.norad ?? "—"} · {t("aos", "捕获", "AOS")}{" "}
                    {new Date(passes[selectedPassIndex].aosIso).toLocaleString(isZh ? "zh-CN" : "en-US")}
                  </p>

                  <div className="mt-6 space-y-3 mb-6">
                    {quote.breakdown.map((item, i) => (
                      <div key={i} className="flex justify-between text-steel-2">
                        <span>{item.desc}</span>
                      </div>
                    ))}
                  </div>

                  <p className="text-xs text-graphite-mute font-mono">
                    {t("no_payment", "本阶段不收取任何费用——本次过境的正式报价将由销售台通过电子邮件发送给您。", "No payment is taken at this stage — a formal quote for this pass will be emailed to you by the sales desk.")}
                  </p>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setStep(2)}
                    className="px-6 py-3.5 border border-graphite-600 font-medium text-steel-2 hover:text-white hover:border-steel transition-colors"
                  >
                    {t("back", "返回", "Back")}
                  </button>
                  <button
                    onClick={handleConfirm}
                    className="flex-1 py-3.5 bg-green hover:bg-green-soft text-graphite font-semibold transition-colors"
                  >
                    {isChecking ? t("requesting", "正在请求...", "Requesting...") : t("request_quote", "申请报价", "Request a Quote")}
                  </button>
                </div>
              </div>
            )}

            {/* STEP 4 · SUCCESS */}
            {step === 4 && (
              <div className="text-center py-10">
                <div className="mx-auto w-20 h-20 bg-green/15 border border-green/50 rounded-full flex items-center justify-center mb-6">
                  <span className="text-3xl font-mono font-bold text-green-soft">✓</span>
                </div>
                <h2 className="font-display font-bold text-3xl text-white mb-3">{t("success_title", "报价申请已提交", "Quote Request Received")}</h2>
                <p className="text-steel-2 mb-10 max-w-md mx-auto leading-relaxed">
                  {t("success_body", "您的申请已被销售台接收。所选过境的正式报价将很快发送给您。", "Your request has been received by the sales desk. A formal quote for the selected pass will be sent to you shortly.")}
                </p>
                <button
                  onClick={() => {
                    setSat(null);
                    setPasses(null);
                    setQuote(null);
                    setSelectedPassIndex(null);
                    setStep(1);
                  }}
                  className="mono-label text-signal-soft hover:text-signal transition-colors"
                  >
                    {t("start_another", "再发起一次申请 →", "START ANOTHER REQUEST →")}
                  </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}