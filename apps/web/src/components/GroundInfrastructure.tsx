import RevealOnScroll from "./RevealOnScroll";

export type GroundInfrastructureText = {
  eyebrow: string;
  title: string;
  subtitle: string;
  stages: { name: string; detail: string }[];
  note: string;
};

const STAGE_COLORS = ["#15171A", "#3A4048", "#8D939B", "#5C7D62", "#E2662F"];

export default function GroundInfrastructure({ text }: { text: GroundInfrastructureText }) {
  return (
    <section id="infrastructure" className="relative z-10 bg-mineral/90 text-graphite py-24 px-6 sm:px-10 lg:px-14">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          {/* Header block */}
          <RevealOnScroll className="lg:col-span-5">
            <span className="mono-label text-signal inline-flex items-center gap-3">
              <span className="w-8 h-px bg-signal" />
              {text.eyebrow}
            </span>
            <h2 className="font-display font-bold text-4xl sm:text-5xl tracking-tight mt-5">
              {text.title}
            </h2>
            <p className="mt-5 text-steel leading-relaxed max-w-md">{text.subtitle}</p>
          </RevealOnScroll>

          {/* Pipeline diagram */}
          <RevealOnScroll delay={150} className="lg:col-span-7">
            <div className="grid-paper border border-mineral-3 p-8 sm:p-10">
            <div className="flex flex-col gap-2">
              {text.stages.map((stage, i) => (
                <div key={stage.name} className="relative">
                  <div className="flex items-center gap-5 border border-mineral-3 bg-white px-6 py-5">
                    <span
                      className="font-mono text-[11px] font-semibold"
                      style={{ color: STAGE_COLORS[i] }}
                    >
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <div className="flex-1">
                      <div className="font-display font-semibold text-lg">{stage.name}</div>
                      <div className="font-mono text-xs text-steel mt-0.5">{stage.detail}</div>
                    </div>
                    <span className="w-2 h-2 rounded-full" style={{ background: STAGE_COLORS[i] }} />
                  </div>
                  {i < text.stages.length - 1 && (
                    <div className="absolute left-1/2 -translate-x-1/2 w-px h-4 bg-mineral-3 ml-[19px]" />
                  )}
                </div>
              ))}
              <p className="font-mono text-[10px] text-steel uppercase tracking-widest mt-6">
                {text.note}
              </p>
            </div>
            </div>
          </RevealOnScroll>
        </div>
      </div>
    </section>
  );
}