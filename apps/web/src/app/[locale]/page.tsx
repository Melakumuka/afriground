import Image from "next/image";
import Link from "next/link";
import { getTranslations } from "next-intl/server";
import StationNetworkMap from "@/components/StationNetworkMap";
import PassSimulatorWidget from "@/components/PassSimulatorWidget";
import FeatureGrid from "@/components/FeatureGrid";

export default async function LandingPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Landing" });

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 overflow-hidden">
      
      {/* ── 1. HERO SECTION ────────────────────────────────────────────────── */}
      <section className="relative min-h-[90vh] flex items-center justify-center pt-12 pb-24 px-4 sm:px-6 lg:px-8 border-b border-slate-800/60">
        
        {/* Background Image & Overlay Gradients */}
        <div className="absolute inset-0 z-0">
          <Image
            src="/hero_ground_station.jpg"
            alt="AfriGround Space Ground Station Dish Array"
            fill
            priority
            className="object-cover opacity-25 scale-105 filter saturate-150"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-slate-950/90 via-slate-950/70 to-slate-950" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-900/20 via-transparent to-transparent pointer-events-none" />
        </div>

        <div className="relative z-10 max-w-6xl mx-auto text-center space-y-8 mt-4">
          
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-900/90 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-bold tracking-wider shadow-lg shadow-cyan-500/10 animate-float">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>{t("hero_badge")}</span>
          </div>

          {/* Main Title */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white max-w-5xl mx-auto leading-[1.1]">
            {t("hero_title_prefix")}
            <span className="gradient-text-cyan">{t("hero_title_accent")}</span>
            {t("hero_title_suffix")}
          </h1>

          {/* Subtitle */}
          <p className="text-lg sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed font-normal">
            {t("hero_subtitle")}
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              href={`/${locale}/booking`}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-600 to-purple-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-base shadow-2xl shadow-cyan-500/30 transition-all hover:scale-105 active:scale-95 flex items-center justify-center gap-3"
            >
              <span>🚀 {t("cta_schedule")}</span>
              <span>→</span>
            </Link>

            <Link
              href="#network"
              className="w-full sm:w-auto px-8 py-4 rounded-xl glass-panel hover:bg-slate-900 text-slate-200 hover:text-white font-semibold text-base border border-slate-700 transition-all flex items-center justify-center gap-2"
            >
              <span>🌐 {t("cta_explore")}</span>
            </Link>
          </div>

          {/* Live Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-16 max-w-5xl mx-auto font-mono">
            <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 text-center">
              <div className="text-3xl sm:text-4xl font-black text-cyan-400">14+</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">{t("stat_nodes")}</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 text-center">
              <div className="text-3xl sm:text-4xl font-black text-emerald-400">99.98%</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">{t("stat_uptime")}</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 text-center">
              <div className="text-3xl sm:text-4xl font-black text-indigo-400">&lt; 45ms</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">{t("stat_latency")}</div>
            </div>

            <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 text-center">
              <div className="text-3xl sm:text-4xl font-black text-purple-400">12,500+</div>
              <div className="text-xs text-slate-400 uppercase tracking-wider mt-1">{t("stat_passes")}</div>
            </div>
          </div>

        </div>
      </section>

      {/* ── 2. PAN-AFRICAN GROUND STATION NETWORK SECTION ───────────────────── */}
      <section id="network" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <span className="px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono font-bold uppercase tracking-wider">
            Federated Infrastructure
          </span>
          <h2 className="text-3xl sm:text-5xl font-black text-white">
            {t("network_title")}
          </h2>
          <p className="text-slate-400 text-base leading-relaxed">
            {t("network_subtitle")}
          </p>
        </div>

        <StationNetworkMap currentLocale={locale} />
      </section>

      {/* ── 3. INTERACTIVE ORBIT & PASS CALCULATOR WIDGET ──────────────────── */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12 border-t border-slate-900">
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <span className="px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold uppercase tracking-wider">
            Live Trial
          </span>
          <h2 className="text-3xl sm:text-5xl font-black text-white">
            {t("simulator_title")}
          </h2>
          <p className="text-slate-400 text-base leading-relaxed">
            {t("simulator_subtitle")}
          </p>
        </div>

        <PassSimulatorWidget currentLocale={locale} />
      </section>

      {/* ── 4. PRODUCT SUITE & CAPABILITIES GRID ───────────────────────────── */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12 border-t border-slate-900">
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <span className="px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-bold uppercase tracking-wider">
            GSaaS Architecture
          </span>
          <h2 className="text-3xl sm:text-5xl font-black text-white">
            {t("features_title")}
          </h2>
          <p className="text-slate-400 text-base leading-relaxed">
            {t("features_subtitle")}
          </p>
        </div>

        <FeatureGrid currentLocale={locale} />
      </section>

      {/* ── 5. DEVELOPER API & CLOUD INGESTION SHOWCASE ───────────────────── */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t border-slate-900">
        <div className="glass-panel p-8 sm:p-12 rounded-3xl border border-cyan-500/20 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center bg-slate-950/80">
          
          {/* Left Text */}
          <div className="lg:col-span-6 space-y-6">
            <span className="px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono font-bold uppercase tracking-wider">
              Developer Ecosystem
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-white">
              {t("api_title")}
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed">
              {t("api_subtitle")}
            </p>

            <div className="space-y-3 font-mono text-xs text-slate-300">
              <div className="flex items-center gap-3 p-3 bg-slate-900 rounded-xl border border-slate-800">
                <span className="text-cyan-400 font-bold">POST</span>
                <span>/api/v1/commercial/predict-and-quote</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-slate-900 rounded-xl border border-slate-800">
                <span className="text-emerald-400 font-bold">WSS</span>
                <span>wss://api.afriground.space/ws/telemetry/station-1</span>
              </div>
            </div>

            <div className="pt-2">
              <Link
                href={`/${locale}/support`}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 text-sm font-mono font-bold transition-all"
              >
                <span>Read OpenAPI Specs</span>
                <span>→</span>
              </Link>
            </div>
          </div>

          {/* Right Code Graphic */}
          <div className="lg:col-span-6 glass-panel rounded-2xl p-6 border border-slate-800 bg-slate-900/95 font-mono text-xs overflow-x-auto shadow-2xl">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800 text-slate-500">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <span>schedule_pass.py</span>
            </div>
            
            <pre className="text-slate-300 leading-relaxed">
              <span className="text-purple-400">import</span> afriground_sdk <span className="text-purple-400">as</span> ag<br/><br/>
              client = ag.Client(api_key=<span className="text-emerald-300">&quot;ag_live_98a72b...&quot;</span>)<br/><br/>
              <span className="text-slate-500"># Predict upcoming pass window</span><br/>
              pass_reservation = client.passes.reserve(<br/>
              &nbsp;&nbsp;norad_cat_id=<span className="text-cyan-300">27424</span>,&nbsp;&nbsp;<span className="text-slate-500"># Aqua Satellite</span><br/>
              &nbsp;&nbsp;station_code=<span className="text-emerald-300">&quot;ENT-1&quot;</span>,&nbsp;&nbsp;<span className="text-slate-500"># Entoto Observatory</span><br/>
              &nbsp;&nbsp;band=<span className="text-emerald-300">&quot;X-band&quot;</span>,<br/>
              &nbsp;&nbsp;downlink_format=<span className="text-emerald-300">&quot;CCSDS_CADU&quot;</span><br/>
              )<br/><br/>
              <span className="text-cyan-400">print</span>(f<span className="text-emerald-300">&quot;Pass Confirmed: &#123;pass_reservation.id&#125;&quot;</span>)<br/>
              <span className="text-cyan-400">print</span>(f<span className="text-emerald-300">&quot;Downlink Stream: &#123;pass_reservation.ws_stream_url&#125;&quot;</span>)
            </pre>
          </div>

        </div>
      </section>

      {/* ── 6. FINAL CALL TO ACTION BANNER ─────────────────────────────────── */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto text-center">
        <div className="glass-panel p-12 sm:p-16 rounded-3xl border border-cyan-500/30 bg-gradient-to-b from-slate-900/90 to-slate-950 relative overflow-hidden space-y-8">
          
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

          <span className="px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-mono text-xs font-bold uppercase tracking-wider">
            Ready For Orbit
          </span>

          <h2 className="text-3xl sm:text-5xl font-black text-white max-w-3xl mx-auto">
            {t("cta_banner_title")}
          </h2>

          <p className="text-slate-300 text-base max-w-2xl mx-auto leading-relaxed">
            {t("cta_banner_subtitle")}
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              href={`/${locale}/booking`}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-base shadow-xl shadow-cyan-500/30 transition-all hover:scale-105"
            >
              {t("cta_launch_app")} →
            </Link>

            <Link
              href={`/${locale}/support`}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white font-semibold text-base border border-slate-700 transition-all"
            >
              {t("cta_contact_sales")}
            </Link>
          </div>

        </div>
      </section>

    </main>
  );
}
