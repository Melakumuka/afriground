import Link from "next/link";
import { getTranslations } from "next-intl/server";
import CinematicBackground from "@/components/CinematicBackground";
import CinematicHero from "@/components/CinematicHero";
import StationNetworkMap from "@/components/StationNetworkMap";
import GroundInfrastructure from "@/components/GroundInfrastructure";
import MissionControlPreview from "@/components/MissionControlPreview";
import DataFlowVisualization from "@/components/DataFlowVisualization";
import PassSimulatorWidget from "@/components/PassSimulatorWidget";
import EarthIntelligence from "@/components/EarthIntelligence";
import EngineeringSection from "@/components/EngineeringSection";
import CoverageSection from "@/components/CoverageSection";
import ProofSection from "@/components/ProofSection";
import RevealOnScroll from "@/components/RevealOnScroll";
import {
  fetchMissions,
  fetchNetworkRanking,
  fetchOrchestrationMetrics,
  fetchSlaViolations,
  type MissionControlLive,
} from "@/lib/api";

export default async function LandingPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Landing" });

  // Phase 4.2 — live operational feed from the FastAPI surface. Every call
  // fails soft; when the API is unreachable the section renders its mock text.
  const [missions, metrics, sla, ranking] = await Promise.all([
    fetchMissions(),
    fetchOrchestrationMetrics(),
    fetchSlaViolations(5),
    fetchNetworkRanking(),
  ]);
  const missionControlLive: MissionControlLive | undefined =
    missions || metrics || sla || ranking
      ? {
          source: "api",
          spacecraft: missions ? `${missions.length} ACTIVE` : undefined,
          contactState: metrics
            ? metrics.outbox.by_status.FAILED > 0
              ? "RETRYING"
              : "OUTBOX HEALTHY"
            : undefined,
          telemetry: sla
            ? sla.length > 0
              ? `${sla.length} VIOLATIONS`
              : "NO VIOLATIONS"
            : undefined,
          alerts: sla?.map((v) => ({
            level: v.status === "VIOLATED" ? "WARNING" : "NOMINAL",
            msg: `${v.sla_type.toUpperCase()} · target ${v.target_value}${v.unit ?? ""} / actual ${v.actual_value}${v.unit ?? ""}`,
          })),
        }
      : undefined;

  return (
    <main className="relative min-h-screen bg-graphite">
      {/* Full-page orbital backdrop: LEO satellite, ENT-01 dish, RF link */}
      <CinematicBackground />

      {/* ── 01 · HERO — editorial layer over the scene ────────────── */}
      <CinematicHero
        locale={locale}
        text={{
          eyebrow: t("hero_eyebrow"),
          titleA: t("hero_title_a"),
          titleB: t("hero_title_b"),
          subtitle: t("hero_subtitle"),
          ctaNetwork: t("cta_schedule"),
          ctaTalk: t("cta_talk"),
          scope: t("scope"),
          scopeValue: t("scope_value"),
          networkLabel: t("hud_live"),
          stationLabel: t("hud_station_label"),
          stationId: t("hud_station_id"),
          position: t("hud_position"),
          rfLabel: t("hud_rf_label"),
          rfValue: t("hud_rf"),
          aosLabel: t("hud_aos"),
          aosValue: t("hud_aos_value"),
          losLabel: t("hud_los"),
          losValue: t("hud_los_value"),
          linkLabel: t("hud_link"),
          linkValue: t("hud_link_value"),
          liveLabel: t("hud_live"),
          simulLabel: t("hud_simul"),
        }}
      />

      {/* ── 02 · NETWORK — federated infrastructure ───────────────── */}
      <section
        id="network"
        className="relative z-10 bg-mineral/90 text-graphite py-24 px-6 sm:px-10 lg:px-14 border-t border-mineral-3/70"
      >
        <div className="max-w-7xl mx-auto space-y-12">
          <RevealOnScroll>
            <div className="max-w-3xl">
              <span className="mono-label text-signal inline-flex items-center gap-3">
                <span className="w-8 h-px bg-signal" />
                {t("network_eyebrow")}
              </span>
              <h2 className="font-display font-bold text-4xl sm:text-5xl tracking-tight mt-5">
                {t("network_title")}
              </h2>
              <p className="mt-5 text-steel leading-relaxed">{t("network_subtitle")}</p>
            </div>
          </RevealOnScroll>
          <RevealOnScroll delay={150}>
            <StationNetworkMap currentLocale={locale} />
          </RevealOnScroll>
        </div>
      </section>

      {/* ── 03 · GROUND INFRASTRUCTURE — technical pipeline ──────── */}
      <GroundInfrastructure
        text={{
          eyebrow: t("infra_eyebrow"),
          title: t("infra_title"),
          subtitle: t("infra_subtitle"),
          note: t("infra_note"),
          stages: t.raw("infra_stages"),
        }}
      />

      {/* ── 04 · MISSION CONTROL — operational interface ─────────── */}
      <MissionControlPreview
        text={{
          eyebrow: t("mission_eyebrow"),
          title: t("mission_title"),
          subtitle: t("mission_subtitle"),
          simulationLabel: t("mission_simulation"),
          liveLabel: t("mission_live"),
          spacecraftLabel: t("mission_spacecraft_label"),
          spacecraftValue: t("mission_spacecraft_value"),
          contactStateLabel: t("mission_contact_label"),
          contactStateValue: t("mission_contact_value"),
          telemetryLabel: t("mission_telemetry_label"),
          telemetryValue: t("mission_telemetry_value"),
          queueLabel: t("mission_queue_label"),
          passScheduleLabel: t("mission_schedule_label"),
          passes: t.raw("mission_passes"),
          queue: t.raw("mission_queue"),
          alerts: t.raw("mission_alerts"),
          alertsLabel: t("mission_alerts_label"),
        }}
        live={missionControlLive}
      />

      {/* ── 05 · DATA — signal to intelligence flow ───────────────── */}
      <section id="data" className="relative z-10 bg-mineral/90 text-graphite">
        <DataFlowVisualization
          text={{
            eyebrow: t("data_eyebrow"),
            title: t("data_title"),
            subtitle: t("data_subtitle"),
            stages: t.raw("data_stages"),
            simulationLabel: t("data_simulation"),
          }}
        />

        {/* Trial harness (dark console on light page) */}
        <div className="relative z-10 bg-mineral/90 px-6 sm:px-10 lg:px-14 pb-24">
          <div className="max-w-7xl mx-auto">
            <div className="console-panel p-8 sm:p-10 relative overflow-hidden">
              <div className="flex items-center gap-3 mb-8">
                <span className="signal-indicator" />
                <span className="mono-label text-signal-soft">{t("data_simulation")}</span>
              </div>
              <PassSimulatorWidget currentLocale={locale} />
            </div>
          </div>
        </div>
      </section>

      {/* ── 06 · EARTH INTELLIGENCE — application index ───────────── */}
      <EarthIntelligence
        text={{
          eyebrow: t("intel_eyebrow"),
          title: t("intel_title"),
          subtitle: t("intel_subtitle"),
          domains: t.raw("intel_domains"),
        }}
      />

      {/* ── 07 · ENGINEERING — specification sheet ────────────────── */}
      <EngineeringSection
        text={{
          eyebrow: t("eng_eyebrow"),
          title: t("eng_title"),
          subtitle: t("eng_subtitle"),
          specs: t.raw("eng_specs"),
          openApiLabel: t("eng_openapi"),
          openApiHref: `/${locale}/support`,
        }}
      />

      {/* ── 08 · GLOBAL NETWORK — coverage topology ───────────────── */}
      <CoverageSection
        text={{
          eyebrow: t("cov_eyebrow"),
          title: t("cov_title"),
          subtitle: t("cov_subtitle"),
          bandLabel: t("cov_bands"),
          bandValue: t("cov_bands_value"),
          backhaulLabel: t("cov_backhaul"),
          backhaulValue: t("cov_backhaul_value"),
          elevationLabel: t("cov_elevation"),
          elevationValue: t("cov_elevation_value"),
          simulationLabel: t("cov_simulation"),
        }}
      />

      {/* ── 09 · PROOF — verified metrics ─────────────────────────── */}
      <ProofSection
        text={{
          eyebrow: t("proof_eyebrow"),
          title: t("proof_title"),
          subtitle: t("proof_subtitle"),
          verifiedLabel: t("proof_verified"),
          placeholderLabel: t("proof_pending"),
          metrics: t.raw("proof_metrics"),
          note: t("proof_note"),
        }}
      />

      {/* ── 10 · CTA — quiet close ────────────────────────────────── */}
      <section className="relative z-10 bg-mineral-2/90 text-graphite py-28 px-6 sm:px-10 lg:px-14 border-t border-mineral-3/70">
        <RevealOnScroll>
          <div className="max-w-4xl mx-auto text-left">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("final_eyebrow")}
          </span>
          <h2 className="font-display font-bold text-5xl sm:text-6xl lg:text-7xl tracking-tight mt-6">
            {t("final_title")}
          </h2>
          <p className="mt-6 text-steel text-lg leading-relaxed max-w-xl">
            {t("final_subtitle")}
          </p>
          <div className="mt-12 flex flex-col sm:flex-row gap-4">
            <Link
              href={`/${locale}/contact`}
              className="px-7 py-3.5 bg-graphite hover:bg-graphite-600 text-white font-semibold text-sm tracking-wide transition-colors"
            >
              {t("final_talk")} →
            </Link>
            <Link
              href={`/${locale}/booking`}
              className="px-7 py-3.5 border border-graphite/30 hover:border-signal/60 text-graphite font-semibold text-sm tracking-wide transition-colors"
            >
              {t("final_platform")}
            </Link>
          </div>
          </div>
        </RevealOnScroll>
      </section>
    </main>
  );
}