"use client";

import ContactForm from "@/components/ContactForm";
import { useT } from "@/lib/useT";

export default function ContactPage() {
  const { t } = useT("Contact");
  return (
    <main className="min-h-screen bg-graphite text-ink">
      {/* ── Ops header ─────────────────────────────────────────── */}
      <div className="border-b border-graphite-600/60">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-14">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("module", "运营模块 05 · 直线联系", "OPS-MODULE 05 · DIRECT LINE")}
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                {t("title", "联系 AfriGround", "Talk to AfriGround")}
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-xl">
                {t("subtitle", "任务咨询、GSaaS 定价、合作请求与技术问题——直接联系运营团队。", "Mission inquiries, GSaaS pricing, partnership requests, and technical questions — reach the operations team directly.")}
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 border border-green/50">
              <span className="w-1.5 h-1.5 rounded-full bg-green-soft animate-pulse" />
              <span className="mono-label text-green-soft">{t("ops_desk", "运营台 · 24/7", "OPS DESK · 24/7")}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 sm:px-10 lg:px-14 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Contact form */}
          <div className="lg:col-span-7">
            <ContactForm />
          </div>

          {/* Direct channels */}
          <div className="lg:col-span-5 space-y-6">
            <div className="console-panel rounded-sm p-6 sm:p-8 border border-graphite-600">
              <span className="mono-label text-signal-soft">{t("direct_channels", "直接渠道", "DIRECT CHANNELS")}</span>
              <ul className="mt-5 space-y-4 text-sm font-mono">
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">{t("ops_label", "运营台", "Operations Desk")}</span>
                  <span className="text-steel-2">ops@afriground.space</span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">{t("sales_label", "销售", "Sales")}</span>
                  <span className="text-steel-2">sales@afriground.space</span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">{t("phone_label", "电话", "Phone")}</span>
                  <span className="text-steel-2">+251 (0) 11 896 1234</span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">{t("sla_label", "响应 SLA", "Response SLA")}</span>
                  <span className="text-green-soft">{t("sla_value", "< 24 小时", "< 24 HOURS")}</span>
                </li>
              </ul>
            </div>

            <div className="rounded-sm border border-graphite-600 bg-graphite-800 p-6">
              <span className="mono-label text-steel-2">{t("what_to_include", "请提供哪些信息", "WHAT TO INCLUDE")}</span>
              <ul className="mt-4 space-y-2.5 text-sm text-steel-2">
                <li>▸ {t("include_1", "任务轨道与频率波段", "Mission orbit & frequency bands")}</li>
                <li>▸ {t("include_2", "每次过境的预计数据量", "Projected data volume per pass")}</li>
                <li>▸ {t("include_3", "发射或首次联络时间线", "Launch or first-contact timeline")}</li>
                <li>▸ {t("include_4", "SLA 或覆盖要求", "Any SLA or coverage requirements")}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}