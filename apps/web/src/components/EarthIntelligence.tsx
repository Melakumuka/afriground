import RevealOnScroll from "./RevealOnScroll";

export type EarthIntelligenceText = {
  eyebrow: string;
  title: string;
  subtitle: string;
  domains: { name: string; note: string }[];
};

export default function EarthIntelligence({ text }: { text: EarthIntelligenceText }) {
  return (
    <section id="intelligence" className="relative z-10 bg-mineral/90 text-graphite py-24 px-6 sm:px-10 lg:px-14">
      <div className="max-w-6xl mx-auto">
        <RevealOnScroll>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end mb-14">
          <div className="lg:col-span-8">
            <span className="mono-label text-signal inline-flex items-center gap-3">
              <span className="w-8 h-px bg-signal" />
              {text.eyebrow}
            </span>
            <h2 className="font-display font-bold text-4xl sm:text-5xl tracking-tight mt-5">
              {text.title}
            </h2>
          </div>
          <div className="lg:col-span-4">
            <p className="text-steel leading-relaxed">{text.subtitle}</p>
          </div>
          </div>
        </RevealOnScroll>

        {/* Editorial application index — not a card grid */}
        <div className="border-t border-mineral-3">
          {text.domains.map((d, i) => (
            <div
              key={d.name}
              className="grid grid-cols-12 gap-4 items-baseline border-b border-mineral-3 py-7 group"
            >
              <span className="col-span-2 sm:col-span-1 font-mono text-sm text-steel">
                {String(i + 1).padStart(2, "0")}
              </span>
              <h3 className="col-span-10 sm:col-span-5 font-display font-semibold text-2xl tracking-tight group-hover:text-signal transition-colors">
                {d.name}
              </h3>
              <p className="col-span-10 sm:col-span-5 col-start-3 sm:col-start-7 font-mono text-xs text-steel leading-relaxed">
                {d.note}
              </p>
              <span className="hidden sm:block col-span-1 text-right font-mono text-steel group-hover:text-signal transition-colors">
                →
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}