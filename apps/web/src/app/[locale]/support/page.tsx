"use client";

import { useState, type FormEvent } from "react";
import { STATIONS } from "@/data/stations";
import { useT } from "@/lib/useT";

export default function SupportPortal() {
  const { t } = useT("Support");
  const [category, setCategory] = useState(t("cat_tech", "技术支持", "Technical Support"));
  const [priority, setPriority] = useState(t("prio_normal", "普通", "Normal"));
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [stationId, setStationId] = useState("none");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "submitted">("idle");
  const [ticketId, setTicketId] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    window.setTimeout(() => {
      setTicketId(`TKT-${String(Math.floor(1000 + Math.random() * 9000))}`);
      setStatus("submitted");
    }, 900);
  };

  const resetForm = () => {
    setCategory(t("cat_tech", "技术支持", "Technical Support"));
    setPriority(t("prio_normal", "普通", "Normal"));
    setEmail("");
    setSubject("");
    setStationId("none");
    setDescription("");
    setStatus("idle");
  };

  const inputCls =
    "w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none";
  const labelCls = "mono-label text-steel-2 block mb-2";

  return (
    <main className="min-h-screen bg-graphite text-ink">
      {/* ── Ops header ─────────────────────────────────────────── */}
      <div className="border-b border-graphite-600/60">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-14">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("module", "运营模块 04 · SLA & 支持", "OPS-MODULE 04 · SLA & SUPPORT")}
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                {t("title", "支持与工单", "Support & Ticketing")}
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-lg">
                {t("subtitle", "为技术事件、账单查询或调度问题创建工单——运营台全天候分诊处理。", "Open a ticket for technical incidents, billing inquiries, or scheduling questions — the ops desk triages around the clock.")}
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 border border-green/50">
              <span className="w-1.5 h-1.5 rounded-full bg-green-soft animate-pulse" />
              <span className="mono-label text-green-soft">{t("ops_desk", "运营台 · 24/7", "OPS DESK · 24/7")}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* New Ticket Form */}
          <div className="lg:col-span-8 w-full console-panel rounded-sm overflow-hidden">
            <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
              <span className="mono-label text-signal-soft">{t("open_ticket", "创建新工单", "OPEN NEW TICKET")}</span>
              <span className="font-mono text-[10px] text-graphite-mute">{t("field_tier1", "一线运营工单", "FIELD · TIER-1 OPS")}</span>
            </div>

            {status === "submitted" ? (
              <div className="p-6 sm:p-10">
                <div className="border border-green/40 bg-green/10 px-6 py-8">
                  <p className="font-mono text-sm text-green-soft font-semibold tracking-wider">
                    ▸ {t("submitted", "工单 {ticket} 已提交", "TICKET {ticket} SUBMITTED").replace("{ticket}", ticketId)}
                  </p>
                  <p className="mt-3 text-sm text-steel-2 leading-relaxed">
                    {t("submitted_body", "工单编号 {ticket} 已转交运营台。确认邮件已发送至 {email}，工程师将按照 {priority} 优先级的 SLA 时限开始处理。", "Reference {ticket} has been routed to the ops desk. A confirmation has been sent to {email} and an engineer will start on it within the SLA window for {priority} priority.")
                      .replace("{ticket}", ticketId)
                      .replace("{email}", email)
                      .replace("{priority}", priority.toUpperCase())}
                  </p>
                </div>
                <button
                  onClick={resetForm}
                  className="mt-6 px-6 py-3.5 bg-signal hover:bg-signal-soft text-graphite font-semibold rounded-sm transition-colors"
                >
                  {t("open_another", "再创建一个工单", "OPEN ANOTHER TICKET")}
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label className={labelCls}>{t("category", "类别", "Category")}</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className={inputCls}
                    >
                      <option>{t("cat_tech", "技术支持", "Technical Support")}</option>
                      <option>{t("cat_billing", "账单与合同", "Billing & Contracts")}</option>
                      <option>{t("cat_schedule", "调度与预订", "Scheduling & Bookings")}</option>
                      <option>{t("cat_partner", "合作与销售", "Partnership & Sales")}</option>
                    </select>
                  </div>
                  <div>
                    <label className={labelCls}>{t("priority", "优先级", "Priority")}</label>
                    <select
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                      className={inputCls}
                    >
                      <option>{t("prio_normal", "普通", "Normal")}</option>
                      <option>{t("prio_high", "高", "High")}</option>
                      <option>{t("prio_urgent", "紧急", "Urgent")}</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label className={labelCls}>{t("contact_email", "联系邮箱 *", "Contact Email *")}</label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@mission.example"
                      className={inputCls}
                    />
                  </div>
                  <div>
                    <label className={labelCls}>{t("related_station", "相关地面站", "Related Station")}</label>
                    <select
                      value={stationId}
                      onChange={(e) => setStationId(e.target.value)}
                      className={inputCls}
                    >
                      <option value="none">{t("none_fleet", "无 / 全网", "None / Fleet-wide")}</option>
                      {STATIONS.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className={labelCls}>{t("subject", "主题 *", "Subject *")}</label>
                  <input
                    type="text"
                    required
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    maxLength={160}
                    placeholder={t("subject_placeholder", "问题的简要概述", "Brief summary of the issue")}
                    className={inputCls}
                  />
                </div>

                <div>
                  <label className={labelCls}>{t("description", "详细描述 *", "Description *")}</label>
                  <textarea
                    required
                    minLength={10}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={7}
                    maxLength={4000}
                    placeholder={t("description_placeholder", "受影响的过境、时间戳、错误信息、天线编号...", "Affected passes, timestamps, error messages, antenna IDs...")}
                    className={`${inputCls} resize-y`}
                  />
                </div>

                <button
                  type="submit"
                  disabled={status === "submitting"}
                  className="w-full py-4 bg-signal hover:bg-signal-soft text-graphite font-semibold rounded-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {status === "submitting" ? (
                    <span className="flex items-center justify-center gap-3">
                      <div className="w-4 h-4 border-2 border-graphite border-t-transparent rounded-full animate-spin" />
                      {t("escalating", "正在升级至一线 ...", "ESCALATING TO TIER-1 ...")}
                    </span>
                  ) : (
                    t("submit", "提交工单 →", "SUBMIT TICKET →")
                  )}
                </button>
              </form>
            )}
          </div>

          {/* Right Column: SLA Matrix + Direct Channels */}
          <div className="lg:col-span-4 space-y-6">
            <div className="console-panel rounded-sm p-6 sm:p-8 border border-graphite-600">
              <span className="mono-label text-signal-soft">{t("severity", "严重级别矩阵 · SLA", "SEVERITY MATRIX · SLA")}</span>
              <ul className="mt-5 space-y-4 text-sm">
                <li className="flex justify-between items-center gap-4">
                  <div>
                    <div className="text-white font-semibold font-mono">{t("urgent", "紧急", "URGENT")}</div>
                    <div className="text-xs text-graphite-mute mt-0.5">{t("urgent_desc", "链路中断 · 服务故障", "Link down · service outage")}</div>
                  </div>
                  <span className="px-2.5 py-1 border border-signal/60 text-signal-soft font-mono text-xs shrink-0">
                    {t("sla_1h", "< 1 小时", "< 1 HOUR")}
                  </span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <div>
                    <div className="text-white font-semibold font-mono">{t("high", "高", "HIGH")}</div>
                    <div className="text-xs text-graphite-mute mt-0.5">{t("high_desc", "服务降级 · 数据丢失", "Degraded service · data loss")}</div>
                  </div>
                  <span className="px-2.5 py-1 border border-signal/40 text-signal/90 font-mono text-xs shrink-0">
                    {t("sla_4h", "< 4 小时", "< 4 HOURS")}
                  </span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <div>
                    <div className="text-white font-semibold font-mono">{t("normal", "普通", "NORMAL")}</div>
                    <div className="text-xs text-graphite-mute mt-0.5">{t("normal_desc", "账单 · 调度 · 咨询", "Billing · scheduling · questions")}</div>
                  </div>
                  <span className="px-2.5 py-1 border border-graphite-600 text-steel-2 font-mono text-xs shrink-0">
                    {t("sla_24h", "< 24 小时", "< 24 HOURS")}
                  </span>
                </li>
              </ul>
            </div>

            <div className="console-panel rounded-sm p-6 sm:p-8 border border-graphite-600">
              <span className="mono-label text-signal-soft">{t("direct_ops", "直接运营渠道", "DIRECT OPS CHANNELS")}</span>
              <ul className="mt-5 space-y-4 text-sm font-mono">
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">{t("ops_label", "运营", "Operations")}</span>
                  <span className="text-steel-2">ops@afriground.space</span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">{t("phone_label", "电话", "Phone")}</span>
                  <span className="text-steel-2">+251 (0) 11 896 1234</span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">{t("outage_label", "故障状态页", "Outage Page")}</span>
                  <span className="text-green-soft">status.afriground.space</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <p className="mono-label text-graphite-mute mt-8">
          {t("footer", "24/7 运营台 · ESA@AFRIGROUND.SPACE · +251 (0) 11 896 1234", "24/7 OPS DESK · ESA@AFRIGROUND.SPACE · +251 (0) 11 896 1234")}
        </p>
      </div>
    </main>
  );
}