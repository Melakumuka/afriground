"use client";

import { useState, type FormEvent } from "react";
import { STATIONS } from "@/data/stations";

export default function SupportPortal() {
  const [category, setCategory] = useState("Technical Support");
  const [priority, setPriority] = useState("Normal");
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
    setCategory("Technical Support");
    setPriority("Normal");
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
            OPS-MODULE 04 · SLA & SUPPORT
          </span>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white">
                Support & Ticketing
              </h1>
              <p className="mt-4 text-steel-2 leading-relaxed max-w-lg">
                Open a ticket for technical incidents, billing inquiries, or scheduling
                questions — the ops desk triages around the clock.
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 border border-green/50">
              <span className="w-1.5 h-1.5 rounded-full bg-green-soft animate-pulse" />
              <span className="mono-label text-green-soft">OPS DESK · 24/7</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* New Ticket Form */}
          <div className="lg:col-span-8 w-full console-panel rounded-sm overflow-hidden">
            <div className="px-6 sm:px-8 py-5 border-b border-graphite-600/60 bg-graphite-700/40 flex items-center justify-between">
              <span className="mono-label text-signal-soft">OPEN NEW TICKET</span>
              <span className="font-mono text-[10px] text-graphite-mute">FIELD · TIER-1 OPS</span>
            </div>

            {status === "submitted" ? (
              <div className="p-6 sm:p-10">
                <div className="border border-green/40 bg-green/10 px-6 py-8">
                  <p className="font-mono text-sm text-green-soft font-semibold tracking-wider">
                    ▸ TICKET {ticketId} SUBMITTED
                  </p>
                  <p className="mt-3 text-sm text-steel-2 leading-relaxed">
                    Reference <span className="text-white font-mono">{ticketId}</span> has been
                    routed to the ops desk. A confirmation has been sent to{" "}
                    <span className="text-white">{email}</span> and an engineer will start on it
                    within the SLA window for{" "}
                    <span className="text-white">{priority.toUpperCase()}</span> priority.
                  </p>
                </div>
                <button
                  onClick={resetForm}
                  className="mt-6 px-6 py-3.5 bg-signal hover:bg-signal-soft text-graphite font-semibold rounded-sm transition-colors"
                >
                  OPEN ANOTHER TICKET
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label className={labelCls}>Category</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className={inputCls}
                    >
                      <option>Technical Support</option>
                      <option>Billing & Contracts</option>
                      <option>Scheduling & Bookings</option>
                      <option>Partnership & Sales</option>
                    </select>
                  </div>
                  <div>
                    <label className={labelCls}>Priority</label>
                    <select
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                      className={inputCls}
                    >
                      <option>Normal</option>
                      <option>High</option>
                      <option>Urgent</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label className={labelCls}>Contact Email *</label>
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
                    <label className={labelCls}>Related Station</label>
                    <select
                      value={stationId}
                      onChange={(e) => setStationId(e.target.value)}
                      className={inputCls}
                    >
                      <option value="none">None / Fleet-wide</option>
                      {STATIONS.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className={labelCls}>Subject *</label>
                  <input
                    type="text"
                    required
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    maxLength={160}
                    placeholder="Brief summary of the issue"
                    className={inputCls}
                  />
                </div>

                <div>
                  <label className={labelCls}>Description *</label>
                  <textarea
                    required
                    minLength={10}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={7}
                    maxLength={4000}
                    placeholder="Affected passes, timestamps, error messages, antenna IDs..."
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
                      ESCALATING TO TIER-1 ...
                    </span>
                  ) : (
                    "SUBMIT TICKET →"
                  )}
                </button>
              </form>
            )}
          </div>

          {/* Right Column: SLA Matrix + Direct Channels */}
          <div className="lg:col-span-4 space-y-6">
            <div className="console-panel rounded-sm p-6 sm:p-8 border border-graphite-600">
              <span className="mono-label text-signal-soft">SEVERITY MATRIX · SLA</span>
              <ul className="mt-5 space-y-4 text-sm">
                <li className="flex justify-between items-center gap-4">
                  <div>
                    <div className="text-white font-semibold font-mono">URGENT</div>
                    <div className="text-xs text-graphite-mute mt-0.5">Link down · service outage</div>
                  </div>
                  <span className="px-2.5 py-1 border border-signal/60 text-signal-soft font-mono text-xs shrink-0">
                    &lt; 1 HOUR
                  </span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <div>
                    <div className="text-white font-semibold font-mono">HIGH</div>
                    <div className="text-xs text-graphite-mute mt-0.5">Degraded service · data loss</div>
                  </div>
                  <span className="px-2.5 py-1 border border-signal/40 text-signal/90 font-mono text-xs shrink-0">
                    &lt; 4 HOURS
                  </span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <div>
                    <div className="text-white font-semibold font-mono">NORMAL</div>
                    <div className="text-xs text-graphite-mute mt-0.5">Billing · scheduling · questions</div>
                  </div>
                  <span className="px-2.5 py-1 border border-graphite-600 text-steel-2 font-mono text-xs shrink-0">
                    &lt; 24 HOURS
                  </span>
                </li>
              </ul>
            </div>

            <div className="console-panel rounded-sm p-6 sm:p-8 border border-graphite-600">
              <span className="mono-label text-signal-soft">DIRECT OPS CHANNELS</span>
              <ul className="mt-5 space-y-4 text-sm font-mono">
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">Operations</span>
                  <span className="text-steel-2">ops@afriground.space</span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">Phone</span>
                  <span className="text-steel-2">+251 (0) 11 896 1234</span>
                </li>
                <li className="flex justify-between items-center gap-4">
                  <span className="text-graphite-mute uppercase">Outage Page</span>
                  <span className="text-green-soft">status.afriground.space</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <p className="mono-label text-graphite-mute mt-8">
          24/7 OPS DESK · ESA@AFRIGROUND.SPACE · +251 (0) 11 896 1234
        </p>
      </div>
    </main>
  );
}