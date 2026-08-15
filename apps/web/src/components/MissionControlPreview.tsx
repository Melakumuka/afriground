import RevealOnScroll from "./RevealOnScroll";

export type MissionControlText = {
  eyebrow: string;
  title: string;
  subtitle: string;
  simulationLabel: string;
  spacecraftLabel: string;
  spacecraftValue: string;
  contactStateLabel: string;
  contactStateValue: string;
  telemetryLabel: string;
  telemetryValue: string;
  queueLabel: string;
  passScheduleLabel: string;
  passes: { sat: string; station: string; aos: string; los: string; state: string }[];
  queue: { cmd: string; target: string; state: string }[];
  alerts: { level: string; msg: string }[];
  alertsLabel: string;
};

export default function MissionControlPreview({ text }: { text: MissionControlText }) {
  return (
    <section id="mission" className="relative z-10 bg-graphite/90 text-ink py-24 px-6 sm:px-10 lg:px-14">
      <div className="max-w-7xl mx-auto">
        <RevealOnScroll>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end mb-14">
            <div className="lg:col-span-8">
              <span className="mono-label text-signal-soft inline-flex items-center gap-3">
                <span className="w-8 h-px bg-signal" />
                {text.eyebrow}
              </span>
              <h2 className="font-display font-bold text-4xl sm:text-5xl tracking-tight text-white mt-5">
                {text.title}
              </h2>
            </div>
            <div className="lg:col-span-4">
              <p className="text-steel leading-relaxed">{text.subtitle}</p>
              <p className="mono-label text-graphite-mute mt-4">
                {text.simulationLabel}
              </p>
            </div>
          </div>
        </RevealOnScroll>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-px bg-graphite-600/60 border border-graphite-600/60">
          {/* Row 1: spacecraft + contact state + telemetry */}
          <div className="lg:col-span-4 console-panel p-7">
            <span className="mono-label text-graphite-mute">{text.spacecraftLabel}</span>
            <div className="font-mono text-2xl font-semibold text-white mt-2">{text.spacecraftValue}</div>
          </div>
          <div className="lg:col-span-4 console-panel p-7 flex items-end justify-between">
            <div>
              <span className="mono-label text-graphite-mute">{text.contactStateLabel}</span>
              <div className="font-mono text-2xl font-semibold mt-2 text-green-soft">
                {text.contactStateValue}
              </div>
            </div>
            <span className="signal-indicator" />
          </div>
          <div className="lg:col-span-4 console-panel p-7">
            <span className="mono-label text-graphite-mute">{text.telemetryLabel}</span>
            <div className="font-mono text-2xl font-semibold text-signal-soft mt-2">
              {text.telemetryValue}
            </div>
          </div>

          {/* Row 2: pass schedule */}
          <div className="lg:col-span-7 console-panel p-7">
            <span className="mono-label text-graphite-mute">{text.passScheduleLabel}</span>
            <div className="mt-4 divide-y divide-graphite-600/60 font-mono text-xs">
              {text.passes.map((p) => (
                <div key={p.sat + p.aos} className="flex items-center gap-4 py-3">
                  <span className="w-24 text-white font-semibold">{p.sat}</span>
                  <span className="w-28 text-graphite-mute">{p.station}</span>
                  <span className="text-steel-2">{p.aos}</span>
                  <span className="text-steel-2">{p.los}</span>
                  <span
                    className={`ml-auto px-2 py-0.5 text-[10px] border ${
                      p.state === "ACTIVE"
                        ? "text-signal-soft border-signal/40"
                        : "text-graphite-mute border-graphite-600"
                    }`}
                  >
                    {p.state}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Command queue */}
          <div className="lg:col-span-5 console-panel p-7">
            <span className="mono-label text-graphite-mute">{text.queueLabel}</span>
            <div className="mt-4 divide-y divide-graphite-600/60 font-mono text-xs">
              {text.queue.map((q) => (
                <div key={q.cmd} className="flex items-center gap-4 py-3">
                  <span className="text-signal-soft font-semibold">{q.cmd}</span>
                  <span className="text-graphite-mute">{q.target}</span>
                  <span className="ml-auto text-steel-2">{q.state}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Alerts strip */}
          <div className="lg:col-span-12 console-panel p-7 border-t border-graphite-600/60">
            <span className="mono-label text-graphite-mute">{text.alertsLabel}</span>
            <div className="mt-4 flex flex-col sm:flex-row gap-3 font-mono text-[11px]">
              {text.alerts.map((a) => (
                <div
                  key={a.msg}
                  className="flex items-center gap-3 px-4 py-2.5 border border-graphite-600 text-steel-2"
                >
                  <span
                    className={`px-1.5 py-0.5 text-[9px] font-semibold ${
                      a.level === "NOMINAL" ? "bg-green/20 text-green-soft" : "bg-signal/20 text-signal-soft"
                    }`}
                  >
                    {a.level}
                  </span>
                  {a.msg}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}