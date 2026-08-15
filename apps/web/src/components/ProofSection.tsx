import RevealOnScroll from "./RevealOnScroll";
import CountUp from "./CountUp";

export type ProofText = {
  eyebrow: string;
  title: string;
  subtitle: string;
  verifiedLabel: string;
  placeholderLabel: string;
  metrics: { label: string; value: string; note: string; verified: boolean }[];
  note: string;
};

export default function ProofSection({ text }: { text: ProofText }) {
  return (
    <section id="proof" className="relative z-10 bg-mineral-2/90 text-graphite py-24 px-6 sm:px-10 lg:px-14 border-t border-mineral-3/70">
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

        <RevealOnScroll delay={150}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-graphite/15 border border-graphite/15">
            {text.metrics.map((m) => (
              <div key={m.label} className="bg-white p-8">
                <div className="flex items-start justify-between gap-4">
                  <span className="mono-label text-steel">{m.label}</span>
                  <span
                    className={`font-mono text-[9px] px-1.5 py-0.5 border ${
                      m.verified
                        ? "text-green border-green/40"
                        : "text-signal border-signal/40"
                    }`}
                  >
                    {m.verified ? text.verifiedLabel : text.placeholderLabel}
                  </span>
                </div>
                <div className="font-display font-bold text-4xl mt-5 tracking-tight">
                  <CountUp value={m.value} />
                </div>
                <div className="font-mono text-[11px] text-steel mt-2">{m.note}</div>
              </div>
            ))}
          </div>
        </RevealOnScroll>

        <p className="mono-label text-steel mt-8">{text.note}</p>
      </div>
    </section>
  );
}