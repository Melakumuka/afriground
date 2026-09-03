import RevealOnScroll from "./RevealOnScroll";

export type DataFlowText = {
  eyebrow: string;
  title: string;
  subtitle: string;
  stages: { name: string; note: string }[];
  simulationLabel: string;
};

export default function DataFlowVisualization({ text }: { text: DataFlowText }) {
  return (
    <div className="relative z-10 bg-mineral/90 text-graphite py-24 px-6 sm:px-10 lg:px-14 overflow-hidden">
      <div className="max-w-6xl mx-auto">
        <RevealOnScroll>
          <div className="text-left max-w-2xl">
            <span className="mono-label text-signal inline-flex items-center gap-3">
              <span className="w-8 h-px bg-signal" />
              {text.eyebrow}
            </span>
            <h2 className="font-display font-bold text-4xl sm:text-5xl tracking-tight mt-5">
              {text.title}
            </h2>
            <p className="mt-5 text-steel leading-relaxed">{text.subtitle}</p>
          </div>
        </RevealOnScroll>

        {/* Flow strip with animated signal */}
        <RevealOnScroll delay={150}>
          <div className="mt-14 grid grid-cols-2 md:grid-cols-5 gap-px bg-mineral-3 border border-mineral-3">
          {text.stages.map((stage, i) => (
            <div key={stage.name} className="bg-white p-7 relative">
              <span className="font-mono text-[11px] text-signal font-semibold">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="font-display font-semibold text-lg mt-3">{stage.name}</div>
              <div className="font-mono text-[11px] text-steel mt-1.5 uppercase tracking-wide">
                {stage.note}
              </div>
              {i < text.stages.length - 1 && (
                <div className="hidden md:flex absolute top-1/2 -right-[9px] -translate-y-1/2 z-10 gap-[3px]">
                  <span className="w-[3px] h-[3px] rounded-full bg-signal animate-beam" />
                  <span className="w-[3px] h-[3px] rounded-full bg-signal animate-beam" style={{ animationDelay: "0.3s" }} />
                  <span className="w-[3px] h-[3px] rounded-full bg-signal animate-beam" style={{ animationDelay: "0.6s" }} />
                </div>
              )}
            </div>
          ))}
          </div>
        </RevealOnScroll>

        <p className="mono-label text-steel mt-8">{text.simulationLabel}</p>
      </div>
    </div>
  );
}