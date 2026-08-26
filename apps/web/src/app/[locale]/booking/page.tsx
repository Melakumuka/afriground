"use client";

import { useEffect, useState } from "react";
import { STATIONS } from "@/data/stations";
import { useT } from "@/lib/useT";
import { Mission, MissionProfile, VisibilityOpportunity } from "@/lib/api";

type PassesResponse = {
  ok: boolean;
  data?: VisibilityOpportunity[];
  error?: string;
};

type Quote = {
  total: number;
  breakdown: { desc: string; cost: number }[];
};

const RATE_PER_MIN = 15.0;

export default function BookingWizard() {
  const { t, isZh, ns } = useT("Booking");
  const zhSteps = ["航天器", "过境", "报价与预订"];
  const enSteps = ["Vehicle", "Passes", "Quote & Book"];
  const STEPS: string[] = Array.isArray(ns.steps) ? (ns.steps as string[]) : isZh ? zhSteps : enSteps;
  const [step, setStep] = useState(1);

  // Step 1 · Mission selection
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loadingMissions, setLoadingMissions] = useState(true);
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [selectedProfile, setSelectedProfile] = useState<MissionProfile | null>(null);
  const [stationId, setStationId] = useState("entoto");
  const [elevation, setElevation] = useState(5);
  const [days, setDays] = useState(2);
  const [fetchError, setFetchError] = useState("");

  // Step 2 · Prediction
  const [predicting, setPredicting] = useState(false);
  const [predError, setPredError] = useState("");
  const [passes, setPasses] = useState<VisibilityOpportunity[] | null>(null);
  const [selectedPassIndex, setSelectedPassIndex] = useState<number | null>(null);

  // Step 3 · Quote & Book
  const [quote, setQuote] = useState<Quote | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [reservationId, setReservationId] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/platform/missions");
        const json = await res.json();
        if (json.ok && json.data) {
          setMissions(json.data);
        } else {
          setFetchError(t("err_fetch_missions", "无法加载任务列表", "Failed to load missions"));
        }
      } catch {
        setFetchError(t("err_fetch_missions", "无法加载任务列表", "Failed to load missions"));
      } finally {
        setLoadingMissions(false);
      }
    }
    load();
  }, [t]);

  useEffect(() => {
    async function loadProfile() {
      if (!selectedMission) {
        setSelectedProfile(null);
        return;
      }
      try {
        const res = await fetch(`/api/platform/missions/${selectedMission.id}/profiles`);
        const json = await res.json();
        if (json.ok && json.data && json.data.length > 0) {
          setSelectedProfile(json.data[0]); // Just pick the first/active one for now
        } else {
          setSelectedProfile(null);
        }
      } catch {
        setSelectedProfile(null);
      }
    }
    loadProfile();
  }, [selectedMission]);

  const handlePredict = async () => {
    if (!selectedMission || !selectedProfile) return;
    setPredicting(true);
    setPredError("");
    setPasses(null);
    setSelectedPassIndex(null);
    try {
      const now = new Date();
      const end = new Date(now.getTime() + days * 86400 * 1000);
      
      const res = await fetch("/api/platform/contact/visibility", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          spacecraft_id: selectedMission.spacecraft_id,
          station_ids: stationId,
          start: now.toISOString(),
          end: end.toISOString()
        }),
      });
      const data = (await res.json()) as PassesResponse;
      if (!data.ok || !data.data) {
        setPredError(data.error ?? t("err_engine", "引擎错误", "ENGINE ERROR"));
      } else {
        setPasses(data.data);
        if (data.data.length === 0) setPredError(t("err_no_passes", "所选窗口内无过境", "NO PASSES IN SELECTED WINDOW"));
      }
      setStep(2);
    } catch {
      setPredError(t("err_sgp4", "SGP4 引擎不可达", "SGP4 ENGINE UNREACHABLE"));
      setStep(2);
    }
    setPredicting(false);
  };

  const startQuote = () => {
    if (selectedPassIndex === null || !passes) return;
    const pass = passes[selectedPassIndex];
    setIsChecking(true);
    window.setTimeout(() => {
      const durationMin = pass.duration_seconds / 60;
      const cost = Math.round(durationMin * RATE_PER_MIN * 100) / 100;
      setQuote({
        total: cost,
        breakdown: [
          {
            desc: t("pass_duration_desc", "过境时长（{min} 分钟）", "Pass Duration ({min} min)")
              .replace("{min}", durationMin.toFixed(1)),
            cost,
          },
        ],
      });
      setIsChecking(false);
      setStep(3);
    }, 900);
  };

  const handleConfirm = async () => {
    if (selectedPassIndex === null || !passes || !selectedMission || !selectedProfile) return;
    setIsChecking(true);
    try {
      const pass = passes[selectedPassIndex];
      // 1. Create Contact Opportunity
      let res = await fetch("/api/platform/contact/opportunities", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          visibility_ids: [pass.id],
          mission_profile_id: selectedProfile.id,
        })
      });
      let json = await res.json();
      if (!json.ok || !json.data || json.data.length === 0) throw new Error("Failed to create opportunity");
      const oppId = json.data[0].id;

      // 2. Create Reservation
      res = await fetch("/api/platform/contact/reservations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contact_opportunity_id: oppId,
          spacecraft_id: selectedMission.spacecraft_id,
          mission_id: selectedMission.id,
        })
      });
      json = await res.json();
      if (!json.ok || !json.data) throw new Error("Failed to create reservation");

      setReservationId(json.data.id);
      setStep(4);
    } catch (e) {
      alert("Booking failed. Ensure the ground station capabilities match your mission's RF profile.");
    } finally {
      setIsChecking(false);
    }
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
              <span className="mono-label text-green-soft">{t("live_badge", "GSaaS 星历库 · 实时", "GSaaS Ephemeris · Live")}</span>
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
                      <label className="mono-label text-steel-2 block mb-2">{t("search_label", "您注册的任务", "YOUR REGISTERED MISSIONS")}</label>
                      {loadingMissions ? (
                        <p className="mono-label text-graphite-mute">{t("loading_missions", "正在加载...", "LOADING...")}</p>
                      ) : fetchError ? (
                        <p className="mono-label text-signal-soft">{fetchError}</p>
                      ) : (
                        <div className="space-y-3 max-h-72 overflow-y-auto">
                          {missions.map((m) => (
                            <button
                              key={m.id}
                              onClick={() => setSelectedMission(m)}
                              className={`w-full text-left px-4 py-3 flex items-center justify-between gap-4 border transition-colors ${
                                selectedMission?.id === m.id
                                  ? "border-signal/70 bg-signal/10"
                                  : "border-graphite-600 hover:border-steel bg-graphite/60"
                              }`}
                            >
                              <span className="text-sm text-white font-medium">{m.name}</span>
                              <span className="font-mono text-xs text-steel-2">{m.status.toUpperCase()}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {selectedMission && (
                      <div className="flex flex-col gap-2 mt-4 border border-signal/40 bg-signal/10 px-4 py-3">
                        <div className="flex items-center gap-3">
                          <span className="font-display font-semibold text-white text-sm">{selectedMission.name}</span>
                          <span className="font-mono text-[10px] text-graphite-mute uppercase">ID: {selectedMission.spacecraft_id.split("-")[0]}</span>
                        </div>
                        {selectedProfile ? (
                          <span className="font-mono text-xs text-signal-soft">
                            {t("active_profile", "活动配置: ", "Active Profile: ")}{selectedProfile.name} v{selectedProfile.version}
                          </span>
                        ) : (
                          <span className="font-mono text-xs text-red-400">
                            {t("no_profile", "无活动配置", "NO ACTIVE MISSION PROFILE")}
                          </span>
                        )}
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
                  disabled={!selectedMission || !selectedProfile || predicting}
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
                    {selectedMission && (
                      <>
                        <span className="font-mono text-xs text-steel-2">
                          {selectedMission.name}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                {predError && (
                  <div className="border border-signal/50 bg-signal/10 px-5 py-4">
                    <p className="mono-label text-signal-soft">{predError}</p>
                  </div>
                )}

                {passes && passes.length > 0 && (
                  <div className="space-y-3">
                    {passes.map((p, i) => (
                      <button
                        key={`${p.aos}-${i}`}
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
                                {new Date(p.aos).toLocaleDateString(isZh ? "zh-CN" : "en-US", { timeZone: "UTC", weekday: "short", month: "short", day: "numeric" })}{" "}
                                {new Date(p.aos).toLocaleTimeString(isZh ? "zh-CN" : "en-US", { timeZone: "UTC", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false })} UTC
                              </div>
                              <div className="font-mono text-xs text-graphite-mute mt-0.5">
                                {t("los", "结束", "LOS")} {new Date(p.los).toLocaleTimeString(isZh ? "zh-CN" : "en-US", { timeZone: "UTC", hour: "2-digit", minute: "2-digit", hour12: false })} UTC
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-5 font-mono text-sm">
                            <div className="text-right">
                              <div className="text-steel-2">{(p.duration_seconds / 60).toFixed(1)} {t("min", "分钟", "min")}</div>
                              <div className="text-[10px] text-graphite-mute uppercase tracking-wider">{t("duration", "持续时长", "Duration")}</div>
                            </div>
                            <div className="text-right">
                              <div className="text-green-soft">{p.max_elevation_deg.toFixed(1)}°</div>
                              <div className="text-[10px] text-graphite-mute uppercase tracking-wider">{t("max_el", "最大仰角", "Max El")}</div>
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
            {step === 3 && quote && selectedPassIndex !== null && passes && selectedMission && (
              <div className="space-y-8">
                <span className="mono-label text-signal-soft">{t("review_quote", "查看并申请报价", "REVIEW & REQUEST QUOTE")}</span>

                <div className="p-6 sm:p-8 border border-graphite-600 bg-graphite">
                  <span className="mono-label text-steel-2">{t("selected_pass", "已选过境", "SELECTED PASS")}</span>
                  <p className="mt-3 font-mono text-xs text-graphite-mute">
                    {selectedMission.name} · {t("aos", "捕获", "AOS")}{" "}
                    {new Date(passes[selectedPassIndex].aos).toLocaleString(isZh ? "zh-CN" : "en-US")}
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
                <h2 className="font-display font-bold text-3xl text-white mb-3">{t("success_title", "预订成功", "Reservation Confirmed")}</h2>
                <p className="text-steel-2 mb-10 max-w-md mx-auto leading-relaxed">
                  {t("success_body", "您的过境预订已被系统接纳。后台编排引擎将自动将其转为作业。预订ID：", "Your pass reservation has been accepted. The backend orchestrator will automatically convert it into a job. Reservation ID:")} 
                  <br/><span className="text-xs font-mono text-signal-soft">{reservationId}</span>
                </p>
                <button
                  onClick={() => {
                    setSelectedMission(null);
                    setPasses(null);
                    setQuote(null);
                    setSelectedPassIndex(null);
                    setReservationId(null);
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