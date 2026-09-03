"use client";

import { useState, useId, type FormEvent } from "react";
import { STATIONS } from "@/data/stations";
import { useT } from "@/lib/useT";

export interface TicketLog {
  id: string;
  timestamp: string;
  author: string;
  role: "engineer" | "customer" | "system";
  message: string;
  statusChange?: string;
}

export interface SupportTicketItem {
  id: string;
  category: "technical" | "billing" | "scheduling" | "hardware";
  priority: "urgent" | "high" | "normal" | "low";
  status: "open" | "triaged" | "investigating" | "in_progress" | "resolved" | "closed";
  subject: string;
  description: string;
  email: string;
  stationId: string;
  stationName?: string;
  createdAt: string;
  updatedAt: string;
  assignedEngineer?: string;
  slaTargetHours: number;
  logs: TicketLog[];
}

const STORAGE_KEY = "afriground_support_tickets_v1";

const INITIAL_DEMO_TICKETS: SupportTicketItem[] = [
  {
    id: "TKT-8942",
    category: "technical",
    priority: "high",
    status: "investigating",
    subject: "X-Band Demodulator Bit Slip on Sentinel-2A Pass #8421",
    description: "During the 14:22 UTC pass over Entoto Observatory, the CORTEX HDR demodulator reported 4 frame lock dropouts resulting in 1.4% payload loss. Requesting IQ raw dump replay and LNA calibration verification.",
    email: "missions@copernicus-client.eu",
    stationId: "entoto",
    stationName: "Entoto Space Observatory (Ethiopia)",
    createdAt: "2026-08-29T08:15:00Z",
    updatedAt: "2026-08-29T09:40:00Z",
    assignedEngineer: "Eng. Dawit T. (Tier-1 Flight Ops Lead, Entoto Hub)",
    slaTargetHours: 4,
    logs: [
      {
        id: "log-1",
        timestamp: "2026-08-29T08:15:00Z",
        author: "Client Mission Operator",
        role: "customer",
        message: "Ticket opened with affected pass metadata and telemetry logs attached.",
        statusChange: "open",
      },
      {
        id: "log-2",
        timestamp: "2026-08-29T08:32:00Z",
        author: "Ops Desk Automator",
        role: "system",
        message: "Automatic triage: Pass #8421 execution receipt retrieved. RF Eb/N0 dipped to 8.2 dB at 14:26 UTC.",
        statusChange: "triaged",
      },
      {
        id: "log-3",
        timestamp: "2026-08-29T09:40:00Z",
        author: "Eng. Dawit T.",
        role: "engineer",
        message: "Assigned to station RF bench. Inspecting feedhorn polarization angle and checking local weather doppler radar. Initial check shows mild atmospheric scintillation.",
        statusChange: "investigating",
      },
    ],
  },
  {
    id: "TKT-9104",
    category: "hardware",
    priority: "urgent",
    status: "in_progress",
    subject: "Malindi Space Center Dish #2 Azimuth Drive Interlock Alert",
    description: "ACU reported mechanical limit switch warning during pre-pass slew for Terra pass at 06:10 UTC. Pass was rerouted to Hartebeesthoek. Need maintenance clearance report before next scheduled pass.",
    email: "flightops@eumetsat-partner.org",
    stationId: "malindi",
    stationName: "Malindi Space Center (Kenya)",
    createdAt: "2026-08-29T06:25:00Z",
    updatedAt: "2026-08-29T07:15:00Z",
    assignedEngineer: "Eng. Joseph K. (Senior Station Systems Engineer)",
    slaTargetHours: 1,
    logs: [
      {
        id: "log-1",
        timestamp: "2026-08-29T06:25:00Z",
        author: "Automated Safety System",
        role: "system",
        message: "Emergency interlock triggered. ACU slew aborted safely. Reroute dispatch executed.",
        statusChange: "open",
      },
      {
        id: "log-2",
        timestamp: "2026-08-29T06:40:00Z",
        author: "Ops Desk Tier-1",
        role: "engineer",
        message: "Escalated to local ground crew at Malindi. Physical limit switch inspection underway.",
        statusChange: "in_progress",
      },
      {
        id: "log-3",
        timestamp: "2026-08-29T07:15:00Z",
        author: "Eng. Joseph K.",
        role: "engineer",
        message: "Lubrication and encoder recalibration complete. Running 360-degree dry tracking test. Clearance expected in 45 minutes.",
      },
    ],
  },
  {
    id: "TKT-7631",
    category: "billing",
    priority: "normal",
    status: "resolved",
    subject: "Q3 Reserved Pass Capacity True-Up and Overage Reconciliation",
    description: "Requesting breakdown of the 12 additional X-Band downlinks consumed in July under Enterprise GSaaS Contract #ET-2026-C09.",
    email: "accounts@african-earth-obs.org",
    stationId: "none",
    stationName: "All Fleet Hubs",
    createdAt: "2026-08-27T11:00:00Z",
    updatedAt: "2026-08-28T14:30:00Z",
    assignedEngineer: "Bethlehem A. (Commercial Accounts Desk)",
    slaTargetHours: 24,
    logs: [
      {
        id: "log-1",
        timestamp: "2026-08-27T11:00:00Z",
        author: "Finance Team",
        role: "customer",
        message: "Inquiry submitted regarding invoice line item #8812.",
        statusChange: "open",
      },
      {
        id: "log-2",
        timestamp: "2026-08-28T14:30:00Z",
        author: "Bethlehem A.",
        role: "engineer",
        message: "Itemized pass logs and CDR receipts sent via encrypted billing portal. Applied 5% multi-station volume discount rebate. Ticket marked resolved.",
        statusChange: "resolved",
      },
    ],
  },
];

export default function SupportPortal() {
  const { t } = useT("Support");
  const uniqueId = useId();

  // Tab State
  const [activeTab, setActiveTab] = useState<"create" | "history" | "lookup">("create");

  // Form State
  const [category, setCategory] = useState(t("cat_tech", "技术支持", "Technical Support"));
  const [priority, setPriority] = useState(t("prio_normal", "普通", "Normal"));
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [stationId, setStationId] = useState("none");
  const [description, setDescription] = useState("");
  const [formStatus, setFormStatus] = useState<"idle" | "submitting" | "submitted">("idle");
  const [submittedTicketId, setSubmittedTicketId] = useState("");

  // Tickets List State
  const [tickets, setTickets] = useState<SupportTicketItem[]>(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (Array.isArray(parsed) && parsed.length > 0) {
            return parsed;
          }
        }
      } catch {
        // Ignore JSON parse error
      }
    }
    return INITIAL_DEMO_TICKETS;
  });
  const [selectedTicketId, setSelectedTicketId] = useState<string | null>(null);
  const [expandedTicketId, setExpandedTicketId] = useState<string | null>(null);

  // Filters State
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [filterPriority, setFilterPriority] = useState<string>("ALL");
  const [filterCategory, setFilterCategory] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Lookup Tab State
  const [lookupQuery, setLookupQuery] = useState("");
  const [lookupResult, setLookupResult] = useState<SupportTicketItem | null | undefined>(undefined);

  // Note Reply State
  const [replyMessage, setReplyMessage] = useState("");
  const [isPostingReply, setIsPostingReply] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const CATEGORY_CODES: Record<string, "technical" | "billing" | "scheduling" | "hardware"> = {
    "技术支持": "technical",
    "Technical Support": "technical",
    "账单与合同": "billing",
    "Billing & Contracts": "billing",
    "调度与预订": "scheduling",
    "Scheduling & Bookings": "scheduling",
    "合作与销售": "hardware",
    "Partnership & Sales": "hardware",
  };

  const PRIORITY_CODES: Record<string, "urgent" | "high" | "normal" | "low"> = {
    "普通": "normal",
    "Normal": "normal",
    "高": "high",
    "High": "high",
    "紧急": "urgent",
    "Urgent": "urgent",
    "低": "low",
    "Low": "low",
  };

  const SLA_HOURS: Record<string, number> = {
    urgent: 1,
    high: 4,
    normal: 24,
    low: 48,
  };

  // Save tickets helper
  const updateTicketsStorage = (updated: SupportTicketItem[]) => {
    setTickets(updated);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch {
      // Ignore localStorage write error
    }
  };

  // Handle Form Submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormStatus("submitting");

    const catCode = CATEGORY_CODES[category] ?? "technical";
    const prioCode = PRIORITY_CODES[priority] ?? "normal";
    const targetStation = STATIONS.find((s) => s.id === stationId);
    const stationName = targetStation ? targetStation.name : "None / Fleet-wide";

    let generatedId = `TKT-${String(Math.floor(1000 + Math.random() * 9000))}`;

    try {
      const res = await fetch("/api/platform/support/tickets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category: catCode,
          priority: prioCode,
          subject: subject || "Website inquiry",
          description: `${description}\n\nContact: ${email}\nStation: ${stationId}`,
        }),
      });
      const payload = await res.json();
      if (res.ok && payload?.ok && payload?.data?.id) {
        generatedId = `TKT-${payload.data.id.slice(0, 8).toUpperCase()}`;
      }
    } catch {
      // Fallback to random ID
    }

    const newTicket: SupportTicketItem = {
      id: generatedId,
      category: catCode,
      priority: prioCode,
      status: "open",
      subject: subject || "Ground Station Operations Inquiry",
      description: description,
      email: email,
      stationId: stationId,
      stationName: stationName,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      assignedEngineer: prioCode === "urgent" ? "Escalated to 24/7 Tier-1 Duty Manager" : "Pending Triaging Engineer Assignment",
      slaTargetHours: SLA_HOURS[prioCode] || 24,
      logs: [
        {
          id: `log-${Date.now()}`,
          timestamp: new Date().toISOString(),
          author: email ? email.split("@")[0] : "Customer",
          role: "customer",
          message: description,
          statusChange: "open",
        },
        {
          id: `log-${Date.now() + 1}`,
          timestamp: new Date().toISOString(),
          author: "Ops Routing Engine",
          role: "system",
          message: `Ticket registered. SLA window for ${prioCode.toUpperCase()} priority initiated (< ${SLA_HOURS[prioCode]}h).`,
          statusChange: "open",
        },
      ],
    };

    const updatedList = [newTicket, ...tickets];
    updateTicketsStorage(updatedList);

    setSubmittedTicketId(generatedId);
    setFormStatus("submitted");
  };

  const resetForm = () => {
    setCategory(t("cat_tech", "技术支持", "Technical Support"));
    setPriority(t("prio_normal", "普通", "Normal"));
    setEmail("");
    setSubject("");
    setStationId("none");
    setDescription("");
    setFormStatus("idle");
  };

  // Add Follow-up Note to Ticket
  const handleAddNote = (ticketIdToUpdate: string) => {
    if (!replyMessage.trim()) return;
    setIsPostingReply(true);

    setTimeout(() => {
      const now = new Date().toISOString();
      const updated = tickets.map((tkt) => {
        if (tkt.id !== ticketIdToUpdate) return tkt;

        const newLog: TicketLog = {
          id: `log-${Date.now()}`,
          timestamp: now,
          author: "Mission Operator (Client)",
          role: "customer",
          message: replyMessage.trim(),
        };

        // If ticket was resolved, reopening or appending
        const newStatus = tkt.status === "resolved" ? "investigating" : tkt.status;

        return {
          ...tkt,
          status: newStatus,
          updatedAt: now,
          logs: [...tkt.logs, newLog],
        };
      });

      updateTicketsStorage(updated);
      setReplyMessage("");
      setIsPostingReply(false);
    }, 400);
  };

  // Lookup Specific Ticket
  const handleLookup = (e: FormEvent) => {
    e.preventDefault();
    if (!lookupQuery.trim()) {
      setLookupResult(null);
      return;
    }
    const cleanQuery = lookupQuery.trim().toUpperCase();
    const found = tickets.find(
      (tkt) =>
        tkt.id.toUpperCase() === cleanQuery ||
        tkt.id.toUpperCase().includes(cleanQuery) ||
        cleanQuery.includes(tkt.id.toUpperCase())
    );
    setLookupResult(found ?? null);
  };

  // Copy Ticket ID
  const copyTicketId = (idToCopy: string) => {
    navigator.clipboard.writeText(idToCopy);
    setCopiedId(idToCopy);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filtered Tickets
  const filteredTickets = tickets.filter((tkt) => {
    if (filterStatus !== "ALL" && tkt.status !== filterStatus.toLowerCase()) return false;
    if (filterPriority !== "ALL" && tkt.priority !== filterPriority.toLowerCase()) return false;
    if (filterCategory !== "ALL" && tkt.category !== filterCategory.toLowerCase()) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchesId = tkt.id.toLowerCase().includes(q);
      const matchesSubj = tkt.subject.toLowerCase().includes(q);
      const matchesDesc = tkt.description.toLowerCase().includes(q);
      const matchesStation = (tkt.stationName || "").toLowerCase().includes(q);
      if (!matchesId && !matchesSubj && !matchesDesc && !matchesStation) return false;
    }
    return true;
  });

  // Calculate Metrics
  const totalCount = tickets.length;
  const activeCount = tickets.filter(
    (t) => t.status === "open" || t.status === "triaged" || t.status === "investigating" || t.status === "in_progress"
  ).length;
  const resolvedCount = tickets.filter((t) => t.status === "resolved" || t.status === "closed").length;

  const getStatusBadge = (status: SupportTicketItem["status"]) => {
    switch (status) {
      case "open":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 border border-amber-500/50 bg-amber-500/10 text-amber-400 font-mono text-[11px] font-semibold rounded-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            {t("status_open", "待分诊", "OPEN")}
          </span>
        );
      case "triaged":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 border border-sky-500/50 bg-sky-500/10 text-sky-400 font-mono text-[11px] font-semibold rounded-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400" />
            {t("status_triaged", "已分诊", "TRIAGED")}
          </span>
        );
      case "investigating":
      case "in_progress":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 border border-signal/60 bg-signal/10 text-signal-soft font-mono text-[11px] font-semibold rounded-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-signal animate-ping" />
            {t("status_in_progress", "处理中", "IN PROGRESS")}
          </span>
        );
      case "resolved":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 border border-green/50 bg-green/10 text-green-soft font-mono text-[11px] font-semibold rounded-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-green-soft" />
            {t("status_resolved", "已解决", "RESOLVED")}
          </span>
        );
      case "closed":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 border border-graphite-600 bg-graphite-700/60 text-steel-2 font-mono text-[11px] rounded-sm">
            {t("status_closed", "已关闭", "CLOSED")}
          </span>
        );
      default:
        return null;
    }
  };

  const getPriorityBadge = (prio: SupportTicketItem["priority"]) => {
    switch (prio) {
      case "urgent":
        return (
          <span className="px-2 py-0.5 border border-red-500/60 bg-red-500/15 text-red-400 font-mono text-[10px] font-bold tracking-wider uppercase rounded-sm">
            {t("urgent", "紧急", "URGENT")} · &lt;1H SLA
          </span>
        );
      case "high":
        return (
          <span className="px-2 py-0.5 border border-signal/50 bg-signal/10 text-signal font-mono text-[10px] font-bold tracking-wider uppercase rounded-sm">
            {t("high", "高", "HIGH")} · &lt;4H SLA
          </span>
        );
      case "normal":
        return (
          <span className="px-2 py-0.5 border border-graphite-600 bg-graphite-800 text-steel-2 font-mono text-[10px] uppercase rounded-sm">
            {t("normal", "普通", "NORMAL")} · &lt;24H
          </span>
        );
      case "low":
        return (
          <span className="px-2 py-0.5 border border-graphite-600 bg-graphite-800/40 text-graphite-mute font-mono text-[10px] uppercase rounded-sm">
            LOW · &lt;48H
          </span>
        );
    }
  };

  const getCategoryBadge = (cat: SupportTicketItem["category"]) => {
    const map: Record<string, { label: string; color: string }> = {
      technical: { label: "RF / TECH", color: "text-signal-soft border-signal/40" },
      billing: { label: "BILLING", color: "text-green-soft border-green/40" },
      scheduling: { label: "SCHEDULING", color: "text-sky-400 border-sky-400/40" },
      hardware: { label: "HARDWARE / ACU", color: "text-amber-400 border-amber-400/40" },
    };
    const c = map[cat] ?? { label: cat.toUpperCase(), color: "text-steel-2 border-graphite-600" };
    return (
      <span className={`px-2 py-0.5 border ${c.color} bg-graphite-800 font-mono text-[10px] uppercase rounded-sm`}>
        {c.label}
      </span>
    );
  };

  const inputCls =
    "w-full px-4 py-3 bg-graphite border border-graphite-600 text-ink rounded-sm focus:border-signal/70 focus:outline-none";
  const labelCls = "mono-label text-steel-2 block mb-2";

  return (
    <main className="min-h-screen bg-graphite text-ink">
      {/* ── Ops Header ─────────────────────────────────────────── */}
      <div className="border-b border-graphite-600/60">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-12 sm:py-14">
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {t("module", "运营模块 04 · SLA & 支持", "OPS-MODULE 04 · SLA & SUPPORT")}
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-3xl sm:text-4xl lg:text-5xl tracking-tight text-white">
                {t("title", "支持与工单", "Support & Ticketing")}
              </h1>
              <p className="mt-3 text-steel-2 leading-relaxed max-w-xl text-sm sm:text-base">
                {t(
                  "subtitle",
                  "为技术事件、账单查询或调度问题创建工单——运营台全天候分诊处理，实时跟踪处置状态。",
                  "Open a ticket for technical incidents, billing inquiries, or scheduling questions — the ops desk triages around the clock."
                )}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 border border-green/50 bg-green/5 rounded-sm">
                <span className="w-2 h-2 rounded-full bg-green-soft animate-pulse" />
                <span className="mono-label text-green-soft font-semibold">{t("ops_desk", "运营台 · 24/7", "OPS DESK · 24/7")}</span>
              </div>
            </div>
          </div>

          {/* ── Top Navigation Tabs ──────────────────────────────────── */}
          <div className="mt-8 pt-4 border-t border-graphite-600/40 flex flex-wrap gap-2 sm:gap-3">
            <button
              type="button"
              onClick={() => setActiveTab("create")}
              className={`px-4 py-2.5 text-xs sm:text-sm font-mono tracking-wider font-semibold rounded-sm transition-all flex items-center gap-2 cursor-pointer ${
                activeTab === "create"
                  ? "bg-signal text-graphite shadow-md shadow-signal/20 border border-signal"
                  : "text-steel-2 hover:text-white bg-graphite-800/80 hover:bg-graphite-700/80 border border-graphite-600/60"
              }`}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              <span>{t("tab_create", "创建工单", "OPEN NEW TICKET")}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("history")}
              className={`px-4 py-2.5 text-xs sm:text-sm font-mono tracking-wider font-semibold rounded-sm transition-all flex items-center gap-2 cursor-pointer ${
                activeTab === "history"
                  ? "bg-signal text-graphite shadow-md shadow-signal/20 border border-signal"
                  : "text-steel-2 hover:text-white bg-graphite-800/80 hover:bg-graphite-700/80 border border-graphite-600/60"
              }`}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              <span>{t("tab_history", "工单历史与状态跟踪", "TICKET HISTORY & STATUS")}</span>
              {activeCount > 0 && (
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                    activeTab === "history" ? "bg-graphite text-signal-soft" : "bg-signal/20 text-signal-soft"
                  }`}
                >
                  {activeCount}
                </span>
              )}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("lookup")}
              className={`px-4 py-2.5 text-xs sm:text-sm font-mono tracking-wider font-semibold rounded-sm transition-all flex items-center gap-2 cursor-pointer ${
                activeTab === "lookup"
                  ? "bg-signal text-graphite shadow-md shadow-signal/20 border border-signal"
                  : "text-steel-2 hover:text-white bg-graphite-800/80 hover:bg-graphite-700/80 border border-graphite-600/60"
              }`}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <span>{t("tab_lookup", "工单号快速查询", "LOOKUP BY ID")}</span>
            </button>
          </div>
        </div>
      </div>

      {/* ── Main Content Body ────────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-10">
        
        {/* ========================================================================= */}
        {/* TAB 1: CREATE NEW TICKET                                                 */}
        {/* ========================================================================= */}
        {activeTab === "create" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Form */}
            <div className="lg:col-span-8 w-full console-panel rounded-sm overflow-hidden border border-graphite-600/80">
              <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
                <span className="mono-label text-signal-soft">{t("open_ticket", "创建新工单", "OPEN NEW TICKET")}</span>
                <span className="font-mono text-[10px] text-graphite-mute">{t("field_tier1", "一线运营工单", "FIELD · TIER-1 OPS")}</span>
              </div>

              {formStatus === "submitted" ? (
                <div className="p-6 sm:p-10">
                  <div className="border border-green/40 bg-green/10 p-6 sm:p-8 rounded-sm">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                      <p className="font-mono text-base text-green-soft font-bold tracking-wider">
                        ▸ {t("submitted", "工单 {ticket} 已提交", "TICKET {ticket} SUBMITTED").replace("{ticket}", submittedTicketId)}
                      </p>
                      <button
                        type="button"
                        onClick={() => copyTicketId(submittedTicketId)}
                        className="px-2.5 py-1 bg-graphite border border-green/40 text-green-soft hover:text-white text-xs font-mono rounded transition-colors flex items-center gap-1.5 cursor-pointer"
                      >
                        {copiedId === submittedTicketId ? t("copied", "已复制！", "Copied!") : t("copy_id", "复制工单号", "Copy ID")}
                      </button>
                    </div>
                    <p className="mt-3 text-sm text-steel-2 leading-relaxed">
                      {t(
                        "submitted_body",
                        "工单编号 {ticket} 已转交运营台。确认邮件已发送至 {email}，工程师将按照 {priority} 优先级的 SLA 时限开始处理。",
                        "Reference {ticket} has been routed to the ops desk. A confirmation has been sent to {email} and an engineer will start on it within the SLA window for {priority} priority."
                      )
                        .replace("{ticket}", submittedTicketId)
                        .replace("{email}", email || "registered mission contact")
                        .replace("{priority}", priority.toUpperCase())}
                    </p>
                  </div>

                  <div className="mt-6 flex flex-wrap items-center gap-4">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedTicketId(submittedTicketId);
                        setExpandedTicketId(submittedTicketId);
                        setActiveTab("history");
                      }}
                      className="px-6 py-3 bg-signal hover:bg-signal-soft text-graphite font-bold font-mono text-xs uppercase tracking-wider rounded-sm transition-all shadow-md shadow-signal/20 cursor-pointer"
                    >
                      {t("view_history_cta", "在工单历史中查看与跟踪 →", "VIEW IN TICKET HISTORY →")}
                    </button>
                    <button
                      type="button"
                      onClick={resetForm}
                      className="px-6 py-3 border border-graphite-600 hover:border-graphite-500 text-steel-2 hover:text-white font-mono text-xs uppercase tracking-wider rounded-sm transition-colors cursor-pointer"
                    >
                      {t("open_another", "再创建一个工单", "OPEN ANOTHER TICKET")}
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label htmlFor={`cat-${uniqueId}`} className={labelCls}>{t("category", "类别", "Category")}</label>
                      <select
                        id={`cat-${uniqueId}`}
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
                      <label htmlFor={`prio-${uniqueId}`} className={labelCls}>{t("priority", "优先级", "Priority")}</label>
                      <select
                        id={`prio-${uniqueId}`}
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
                      <label htmlFor={`email-${uniqueId}`} className={labelCls}>{t("contact_email", "联系邮箱 *", "Contact Email *")}</label>
                      <input
                        id={`email-${uniqueId}`}
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="you@mission.example"
                        className={inputCls}
                      />
                    </div>
                    <div>
                      <label htmlFor={`station-${uniqueId}`} className={labelCls}>{t("related_station", "相关地面站", "Related Station")}</label>
                      <select
                        id={`station-${uniqueId}`}
                        value={stationId}
                        onChange={(e) => setStationId(e.target.value)}
                        className={inputCls}
                      >
                        <option value="none">{t("none_fleet", "无 / 全网", "None / Fleet-wide")}</option>
                        {STATIONS.map((s) => (
                          <option key={s.id} value={s.id}>
                            {s.name} ({s.country})
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label htmlFor={`subj-${uniqueId}`} className={labelCls}>{t("subject", "主题 *", "Subject *")}</label>
                    <input
                      id={`subj-${uniqueId}`}
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
                    <label htmlFor={`desc-${uniqueId}`} className={labelCls}>{t("description", "详细描述 *", "Description *")}</label>
                    <textarea
                      id={`desc-${uniqueId}`}
                      required
                      minLength={10}
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={6}
                      maxLength={4000}
                      placeholder={t(
                        "description_placeholder",
                        "受影响的过境、时间戳、错误信息、天线编号...",
                        "Affected passes, timestamps, error messages, antenna IDs..."
                      )}
                      className={`${inputCls} resize-y`}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={formStatus === "submitting"}
                    className="w-full py-4 bg-signal hover:bg-signal-soft text-graphite font-bold font-mono text-sm uppercase tracking-wider rounded-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                  >
                    {formStatus === "submitting" ? (
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

            {/* Right Column: Severity Matrix & Direct Channels */}
            <div className="lg:col-span-4 space-y-6">
              <div className="console-panel rounded-sm p-6 sm:p-8 border border-graphite-600">
                <span className="mono-label text-signal-soft">{t("severity", "严重级别矩阵 · SLA", "SEVERITY MATRIX · SLA")}</span>
                <ul className="mt-5 space-y-4 text-sm">
                  <li className="flex justify-between items-center gap-4">
                    <div>
                      <div className="text-white font-semibold font-mono">{t("urgent", "紧急", "URGENT")}</div>
                      <div className="text-xs text-graphite-mute mt-0.5">{t("urgent_desc", "链路中断 · 服务故障", "Link down · service outage")}</div>
                    </div>
                    <span className="px-2.5 py-1 border border-red-500/60 bg-red-500/10 text-red-400 font-mono text-xs shrink-0 font-bold">
                      {t("sla_1h", "< 1 小时", "< 1 HOUR")}
                    </span>
                  </li>
                  <li className="flex justify-between items-center gap-4">
                    <div>
                      <div className="text-white font-semibold font-mono">{t("high", "高", "HIGH")}</div>
                      <div className="text-xs text-graphite-mute mt-0.5">{t("high_desc", "服务降级 · 数据丢失", "Degraded service · data loss")}</div>
                    </div>
                    <span className="px-2.5 py-1 border border-signal/60 bg-signal/10 text-signal-soft font-mono text-xs shrink-0 font-semibold">
                      {t("sla_4h", "< 4 小时", "< 4 HOURS")}
                    </span>
                  </li>
                  <li className="flex justify-between items-center gap-4">
                    <div>
                      <div className="text-white font-semibold font-mono">{t("normal", "普通", "NORMAL")}</div>
                      <div className="text-xs text-graphite-mute mt-0.5">{t("normal_desc", "账单 · 调度 · 咨询", "Billing · scheduling · questions")}</div>
                    </div>
                    <span className="px-2.5 py-1 border border-graphite-600 bg-graphite-800 text-steel-2 font-mono text-xs shrink-0">
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
        )}

        {/* ========================================================================= */}
        {/* TAB 2: TICKET HISTORY & STATUS UPDATES                                    */}
        {/* ========================================================================= */}
        {activeTab === "history" && (
          <div className="space-y-8">
            {/* Summary Metrics Bar */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="console-panel p-5 rounded-sm border border-graphite-600/70">
                <span className="mono-label text-graphite-mute text-[11px]">{t("stat_total", "工单总数", "TOTAL TICKETS")}</span>
                <div className="mt-2 text-2xl sm:text-3xl font-display font-bold text-white">{totalCount}</div>
              </div>
              <div className="console-panel p-5 rounded-sm border border-signal/40 bg-signal/5">
                <span className="mono-label text-signal-soft text-[11px]">{t("stat_active", "处理中工单", "ACTIVE & IN PROGRESS")}</span>
                <div className="mt-2 text-2xl sm:text-3xl font-display font-bold text-signal-soft">{activeCount}</div>
              </div>
              <div className="console-panel p-5 rounded-sm border border-green/40 bg-green/5">
                <span className="mono-label text-green-soft text-[11px]">{t("stat_resolved", "已解决", "RESOLVED")}</span>
                <div className="mt-2 text-2xl sm:text-3xl font-display font-bold text-green-soft">{resolvedCount}</div>
              </div>
              <div className="console-panel p-5 rounded-sm border border-graphite-600/70">
                <span className="mono-label text-graphite-mute text-[11px]">{t("stat_sla_compliance", "SLA 达成率", "SLA COMPLIANCE")}</span>
                <div className="mt-2 text-2xl sm:text-3xl font-display font-bold text-white">99.4%</div>
              </div>
            </div>

            {/* Filter and Search Bar */}
            <div className="console-panel p-5 rounded-sm border border-graphite-600/80 flex flex-col md:flex-row gap-4 justify-between items-stretch md:items-center">
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-graphite-mute">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t("search_placeholder", "按工单号、主题或描述搜索...", "Search tickets by ID, subject, or description...")}
                  className="w-full pl-10 pr-4 py-2.5 bg-graphite border border-graphite-600 text-sm text-ink rounded-sm focus:border-signal/70 focus:outline-none font-mono"
                />
              </div>

              <div className="flex flex-wrap gap-2.5 items-center">
                {/* Status Filter */}
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 bg-graphite border border-graphite-600 text-xs font-mono text-steel-2 rounded-sm focus:outline-none focus:border-signal/70"
                >
                  <option value="ALL">{t("all_statuses", "所有状态", "All Statuses")}</option>
                  <option value="OPEN">Open</option>
                  <option value="TRIAGED">Triaged</option>
                  <option value="INVESTIGATING">Investigating</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="RESOLVED">Resolved</option>
                </select>

                {/* Priority Filter */}
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                  className="px-3 py-2 bg-graphite border border-graphite-600 text-xs font-mono text-steel-2 rounded-sm focus:outline-none focus:border-signal/70"
                >
                  <option value="ALL">{t("all_priorities", "所有优先级", "All Priorities")}</option>
                  <option value="URGENT">Urgent (&lt;1h)</option>
                  <option value="HIGH">High (&lt;4h)</option>
                  <option value="NORMAL">Normal (&lt;24h)</option>
                  <option value="LOW">Low (&lt;48h)</option>
                </select>

                {/* Category Filter */}
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="px-3 py-2 bg-graphite border border-graphite-600 text-xs font-mono text-steel-2 rounded-sm focus:outline-none focus:border-signal/70"
                >
                  <option value="ALL">{t("all_categories", "所有类别", "All Categories")}</option>
                  <option value="TECHNICAL">Technical / RF</option>
                  <option value="BILLING">Billing</option>
                  <option value="SCHEDULING">Scheduling</option>
                  <option value="HARDWARE">Hardware / ACU</option>
                </select>

                {(filterStatus !== "ALL" || filterPriority !== "ALL" || filterCategory !== "ALL" || searchQuery) && (
                  <button
                    type="button"
                    onClick={() => {
                      setFilterStatus("ALL");
                      setFilterPriority("ALL");
                      setFilterCategory("ALL");
                      setSearchQuery("");
                    }}
                    className="px-2.5 py-2 text-xs font-mono text-signal-soft hover:underline cursor-pointer"
                  >
                    {t("clear_filters", "重置", "Clear")}
                  </button>
                )}
              </div>
            </div>

            {/* Tickets List Feed */}
            {filteredTickets.length === 0 ? (
              <div className="console-panel p-12 text-center border border-graphite-600 rounded-sm">
                <svg
                  width="40"
                  height="40"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  className="mx-auto text-graphite-mute mb-3"
                >
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="9" y1="15" x2="15" y2="15" />
                </svg>
                <div className="text-white font-mono text-sm font-semibold">{t("no_tickets_found", "未找到匹配的工单。", "No tickets matching your filters.")}</div>
                <button
                  type="button"
                  onClick={() => {
                    setFilterStatus("ALL");
                    setFilterPriority("ALL");
                    setFilterCategory("ALL");
                    setSearchQuery("");
                  }}
                  className="mt-4 px-4 py-2 border border-signal text-signal-soft font-mono text-xs rounded-sm hover:bg-signal/10 transition-colors cursor-pointer"
                >
                  {t("clear_filters", "重置筛选条件", "Clear Filters")}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredTickets.map((tkt) => {
                  const isExpanded = expandedTicketId === tkt.id;

                  // Stepper logic
                  const stepIndex =
                    tkt.status === "open"
                      ? 1
                      : tkt.status === "triaged"
                      ? 2
                      : tkt.status === "investigating" || tkt.status === "in_progress"
                      ? 3
                      : 4;

                  return (
                    <div
                      key={tkt.id}
                      className={`console-panel rounded-sm border transition-all ${
                        isExpanded ? "border-signal/70 shadow-lg shadow-black/40" : "border-graphite-600 hover:border-graphite-500"
                      }`}
                    >
                      {/* Ticket Header Card */}
                      <div className="p-5 sm:p-6 cursor-pointer" onClick={() => setExpandedTicketId(isExpanded ? null : tkt.id)}>
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div className="flex flex-wrap items-center gap-2.5">
                            <span className="font-mono text-xs font-bold text-signal-soft tracking-wider px-2 py-0.5 bg-graphite-800 border border-signal/30 rounded">
                              {tkt.id}
                            </span>
                            {getCategoryBadge(tkt.category)}
                            {getPriorityBadge(tkt.priority)}
                            {getStatusBadge(tkt.status)}
                          </div>
                          <div className="text-xs font-mono text-graphite-mute flex items-center gap-2">
                            <span>{new Date(tkt.createdAt).toLocaleDateString()}</span>
                            <span className="text-graphite-600">•</span>
                            <span>{new Date(tkt.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                          </div>
                        </div>

                        <div className="mt-3">
                          <h3 className="text-base sm:text-lg font-bold text-white tracking-tight">{tkt.subject}</h3>
                          <p className="mt-1 text-xs sm:text-sm text-steel-2 line-clamp-2 leading-relaxed">{tkt.description}</p>
                        </div>

                        {/* Station and Assigned Engineer Row */}
                        <div className="mt-4 pt-3 border-t border-graphite-600/50 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
                          <div className="flex items-center gap-3 text-steel-2">
                            <span className="text-graphite-mute">STATION:</span>
                            <span className="text-white">{tkt.stationName || "Fleet-wide / Core"}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-graphite-mute">{t("assigned_to", "责任工程师:", "ASSIGNED:")}</span>
                            <span className="text-signal-soft">{tkt.assignedEngineer || "Tier-1 Ops Desk"}</span>
                            <svg
                              width="16"
                              height="16"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              className={`transition-transform text-steel-2 ${isExpanded ? "rotate-180 text-signal" : ""}`}
                            >
                              <polyline points="6 9 12 15 18 9" />
                            </svg>
                          </div>
                        </div>
                      </div>

                      {/* Expanded Section: Status Stepper, Updates Timeline, Reply Box */}
                      {isExpanded && (
                        <div className="border-t border-graphite-600/80 bg-graphite-800/40 p-5 sm:p-8 space-y-6 animate-fade-up">
                          {/* 4-Step Resolution Progress Visualizer */}
                          <div>
                            <div className="mono-label text-signal-soft mb-3 text-[11px]">
                              {t("status_timeline", "处置进度跟踪 · RESOLUTION PROGRESS", "RESOLUTION PROGRESS TRACKER")}
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono">
                              <div
                                className={`p-3 rounded border ${
                                  stepIndex >= 1
                                    ? "border-signal/60 bg-signal/10 text-signal-soft"
                                    : "border-graphite-600/60 bg-graphite text-graphite-mute"
                                }`}
                              >
                                <div className="font-bold">1. SUBMITTED</div>
                                <div className="text-[10px] text-steel-2 mt-0.5">Payload received</div>
                              </div>
                              <div
                                className={`p-3 rounded border ${
                                  stepIndex >= 2
                                    ? "border-signal/60 bg-signal/10 text-signal-soft"
                                    : "border-graphite-600/60 bg-graphite text-graphite-mute"
                                }`}
                              >
                                <div className="font-bold">2. TRIAGED</div>
                                <div className="text-[10px] text-steel-2 mt-0.5">Assigned to engineer</div>
                              </div>
                              <div
                                className={`p-3 rounded border ${
                                  stepIndex >= 3
                                    ? "border-signal/60 bg-signal/10 text-signal-soft"
                                    : "border-graphite-600/60 bg-graphite text-graphite-mute"
                                }`}
                              >
                                <div className="font-bold">3. IN PROGRESS</div>
                                <div className="text-[10px] text-steel-2 mt-0.5">Diagnostic & recovery</div>
                              </div>
                              <div
                                className={`p-3 rounded border ${
                                  stepIndex >= 4
                                    ? "border-green/60 bg-green/10 text-green-soft"
                                    : "border-graphite-600/60 bg-graphite text-graphite-mute"
                                }`}
                              >
                                <div className="font-bold">4. RESOLVED</div>
                                <div className="text-[10px] text-steel-2 mt-0.5">Closure verified</div>
                              </div>
                            </div>
                          </div>

                          {/* Chronological Ops Updates & Log Feed */}
                          <div>
                            <div className="mono-label text-signal-soft mb-3 text-[11px]">
                              {t("ops_notes", "运营台处置记录与沟通", "OPS DESK DISPATCH LOG & COMMUNICATION")}
                            </div>
                            <div className="space-y-3">
                              {tkt.logs.map((log) => (
                                <div
                                  key={log.id}
                                  className={`p-4 rounded-sm border ${
                                    log.role === "engineer"
                                      ? "border-signal/40 bg-signal/5"
                                      : log.role === "system"
                                      ? "border-graphite-600 bg-graphite-900/60"
                                      : "border-graphite-600/80 bg-graphite-700/30"
                                  }`}
                                >
                                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono mb-2">
                                    <div className="flex items-center gap-2">
                                      <span
                                        className={`font-bold ${
                                          log.role === "engineer"
                                            ? "text-signal-soft"
                                            : log.role === "system"
                                            ? "text-green-soft"
                                            : "text-white"
                                        }`}
                                      >
                                        {log.role === "engineer" ? "🛠️ " : log.role === "system" ? "🤖 " : "👤 "}
                                        {log.author}
                                      </span>
                                      {log.statusChange && (
                                        <span className="px-1.5 py-0.2 bg-graphite-800 border border-graphite-600 text-[10px] text-steel-2 uppercase rounded">
                                          → {log.statusChange}
                                        </span>
                                      )}
                                    </div>
                                    <span className="text-[11px] text-graphite-mute">
                                      {new Date(log.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                  <p className="text-xs sm:text-sm text-steel-2 leading-relaxed font-sans">{log.message}</p>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Add Follow-Up Note / Reply */}
                          <div className="pt-2 border-t border-graphite-600/60">
                            <label className={labelCls}>
                              {t("add_note", "添加跟进说明 / 留言", "ADD FOLLOW-UP NOTE / DISPATCH MESSAGE")}
                            </label>
                            <div className="flex flex-col sm:flex-row gap-3">
                              <textarea
                                value={selectedTicketId === tkt.id ? replyMessage : ""}
                                onChange={(e) => {
                                  setSelectedTicketId(tkt.id);
                                  setReplyMessage(e.target.value);
                                }}
                                onFocus={() => setSelectedTicketId(tkt.id)}
                                rows={2}
                                placeholder={t(
                                  "note_placeholder",
                                  "输入补充信息、过境日志或疑问...",
                                  "Enter additional observations, pass logs, or questions..."
                                )}
                                className={`${inputCls} resize-y text-xs sm:text-sm`}
                              />
                              <button
                                type="button"
                                onClick={() => handleAddNote(tkt.id)}
                                disabled={isPostingReply || !replyMessage.trim() || selectedTicketId !== tkt.id}
                                className="px-6 py-3 bg-signal hover:bg-signal-soft text-graphite font-bold font-mono text-xs uppercase tracking-wider rounded-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0 cursor-pointer self-end sm:self-stretch flex items-center justify-center"
                              >
                                {isPostingReply ? (
                                  <div className="w-4 h-4 border-2 border-graphite border-t-transparent rounded-full animate-spin" />
                                ) : (
                                  t("post_update", "提交更新", "POST UPDATE")
                                )}
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: LOOKUP BY TICKET ID                                                */}
        {/* ========================================================================= */}
        {activeTab === "lookup" && (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="console-panel p-6 sm:p-8 rounded-sm border border-graphite-600">
              <span className="mono-label text-signal-soft">{t("lookup_title", "快速查询工单状态", "TRACK SPECIFIC TICKET")}</span>
              <p className="mt-2 text-sm text-steel-2 leading-relaxed">
                {t(
                  "lookup_desc",
                  "输入工单编号（如 TKT-8942 或完整 UUID）查询实时处置进度与处理记录。",
                  "Enter your reference number (e.g., TKT-8942 or full UUID) to retrieve real-time status and telemetry logs."
                )}
              </p>

              <form onSubmit={handleLookup} className="mt-6 flex flex-col sm:flex-row gap-3">
                <input
                  type="text"
                  required
                  value={lookupQuery}
                  onChange={(e) => setLookupQuery(e.target.value)}
                  placeholder="e.g. TKT-8942"
                  className="flex-1 px-4 py-3 bg-graphite border border-graphite-600 text-sm font-mono text-white rounded-sm focus:border-signal/70 focus:outline-none"
                />
                <button
                  type="submit"
                  className="px-6 py-3 bg-signal hover:bg-signal-soft text-graphite font-bold font-mono text-xs uppercase tracking-wider rounded-sm transition-colors cursor-pointer"
                >
                  {t("lookup_btn", "查询工单", "SEARCH TICKET")}
                </button>
              </form>
            </div>

            {/* Lookup Result View */}
            {lookupResult === null && (
              <div className="console-panel p-6 border border-red-500/40 bg-red-500/10 rounded-sm text-sm text-red-300 font-mono">
                {t("ticket_not_found", "未找到该工单编号，请核对工单号或在历史列表中查看。", "Ticket reference not found. Please verify the ID or check the history list.")}
              </div>
            )}

            {lookupResult && (
              <div className="console-panel p-6 sm:p-8 border border-signal rounded-sm space-y-6 animate-fade-up">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="font-mono text-sm font-bold text-signal-soft px-2.5 py-1 bg-graphite border border-signal/40 rounded">
                      {lookupResult.id}
                    </span>
                    {getCategoryBadge(lookupResult.category)}
                    {getPriorityBadge(lookupResult.priority)}
                    {getStatusBadge(lookupResult.status)}
                  </div>
                  <span className="text-xs font-mono text-steel-2">
                    {new Date(lookupResult.createdAt).toLocaleString()}
                  </span>
                </div>

                <div>
                  <h3 className="text-xl font-bold text-white">{lookupResult.subject}</h3>
                  <p className="mt-2 text-sm text-steel-2 leading-relaxed">{lookupResult.description}</p>
                </div>

                <div className="p-4 bg-graphite-800/80 border border-graphite-600 rounded-sm text-xs font-mono space-y-2">
                  <div className="flex justify-between">
                    <span className="text-graphite-mute">STATION:</span>
                    <span className="text-white">{lookupResult.stationName || "Fleet-wide"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-graphite-mute">ASSIGNED ENGINEER:</span>
                    <span className="text-signal-soft">{lookupResult.assignedEngineer || "Tier-1 Ops Lead"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-graphite-mute">SLA TARGET WINDOW:</span>
                    <span className="text-green-soft">&lt; {lookupResult.slaTargetHours} Hours</span>
                  </div>
                </div>

                {/* Progress Log */}
                <div>
                  <div className="mono-label text-signal-soft mb-3 text-[11px]">LATEST ACTIVITY LOG</div>
                  <div className="space-y-3">
                    {lookupResult.logs.map((log) => (
                      <div key={log.id} className="p-3.5 bg-graphite border border-graphite-600/70 rounded text-xs">
                        <div className="flex justify-between font-mono text-[11px] text-graphite-mute mb-1">
                          <span className="text-white font-semibold">{log.author}</span>
                          <span>{new Date(log.timestamp).toLocaleString()}</span>
                        </div>
                        <p className="text-steel-2">{log.message}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    setExpandedTicketId(lookupResult.id);
                    setActiveTab("history");
                  }}
                  className="w-full py-3 border border-signal/60 hover:bg-signal/10 text-signal-soft font-mono text-xs uppercase tracking-wider rounded-sm transition-colors cursor-pointer"
                >
                  {t("view_history_cta", "在完整历史中管理该工单 →", "MANAGE IN FULL TICKET HISTORY →")}
                </button>
              </div>
            )}
          </div>
        )}

        <p className="mono-label text-graphite-mute mt-12 text-center text-xs">
          {t("footer", "24/7 运营台 · ESA@AFRIGROUND.SPACE · +251 (0) 11 896 1234", "24/7 OPS DESK · ESA@AFRIGROUND.SPACE · +251 (0) 11 896 1234")}
        </p>
      </div>
    </main>
  );
}
