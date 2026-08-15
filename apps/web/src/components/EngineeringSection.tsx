import RevealOnScroll from "./RevealOnScroll";

export type EngineeringText = {
  eyebrow: string;
  title: string;
  subtitle: string;
  specs: { unit: string; value: string; note: string }[];
  openApiLabel: string;
  openApiHref: string;
};

export default function EngineeringSection({ text }: { text: EngineeringText }) {
  return (
    <section id="engineering" className="relative z-10 bg-mineral-2/90 text-graphite py-24 px-6 sm:px-10 lg:px-14">
      <div className="max-w-6xl mx-auto">
        <RevealOnScroll>
          <span className="mono-label text-signal inline-flex items-center gap-3">
            <span className="w-8 h-px bg-signal" />
            {text.eyebrow}
          </span>
          <h2 className="font-display font-bold text-4xl sm:text-5xl tracking-tight mt-5 max-w-3xl">
            {text.title}
          </h2>
          <p className="mt-5 text-steel leading-relaxed max-w-2xl">{text.subtitle}</p>
        </RevealOnScroll>

        {/* Specification sheet */}
        <div className="mt-12 border-t border-graphite/20 font-mono text-sm">
          {text.specs.map((s) => (
            <div
              key={s.unit}
              className="grid grid-cols-12 gap-4 items-baseline border-b border-graphite/15 py-5"
            >
              <span className="col-span-4 sm:col-span-3 text-steel">{s.unit}</span>
              <span className="col-span-8 sm:col-span-5 font-semibold text-graphite">{s.value}</span>
              <span className="col-span-12 sm:col-span-4 text-xs text-steel sm:text-right">
                {s.note}
              </span>
            </div>
          ))}
        </div>

        <div className="mt-10 inline-flex items-center gap-3 border border-graphite/25 px-6 py-3 hover:border-signal/50 transition-colors">
          <a href={text.openApiHref} className="text-sm font-semibold tracking-wide">
            {text.openApiLabel}
          </a>
          <span className="text-signal">→</span>
        </div>
      </div>
    </section>
  );
}