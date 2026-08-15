import { STATIONS } from "@/data/stations";
import RevealOnScroll from "./RevealOnScroll";
import CountUp from "./CountUp";

export type CoverageText = {
  eyebrow: string;
  title: string;
  subtitle: string;
  bandLabel: string;
  backhaulLabel: string;
  bandValue: string;
  backhaulValue: string;
  elevationLabel: string;
  elevationValue: string;
  simulationLabel: string;
};

const W = 720;
const H = 720;

const COAST: [number, number][] = [
  [-5.9, 35.8], [-6.0, 34.2], [-6.3, 33.2], [-6.9, 32.3], [-8.1, 31.4],
  [-9.8, 30.3], [-16.0, 24.1], [-17.5, 21.0], [-17.4, 14.7], [-16.2, 12.6],
  [-14.0, 12.7], [-12.0, 11.2], [-13.0, 10.0], [-7.6, 6.4], [-4.8, 5.2],
  [0.6, 5.5], [5.0, 6.2], [7.1, 4.8], [9.8, 4.0], [10.3, 2.4],
  [9.5, 1.6], [9.0, -1.3], [7.5, -3.0], [5.0, -6.5], [4.2, -8.5],
  [3.3, -11.6], [2.6, -15.1], [1.7, -18.4], [1.4, -22.0], [2.4, -24.4],
  [5.6, -27.3], [11.2, -30.2], [14.7, -31.8], [19.5, -34.9], [21.5, -34.4],
  [24.5, -32.7], [28.0, -31.0], [32.0, -32.4], [36.5, -30.8], [41.5, -27.9],
  [46.5, -29.1], [52.0, -26.0], [57.5, -25.7], [62.0, -22.4], [67.0, -25.6],
  [70.0, -23.5], [75.0, -22.8], [80.0, -25.8], [85.0, -24.0], [90.0, -22.0],
  [100.0, -23.8], [105.0, -23.4], [112.0, -26.4], [116.0, -23.2], [120.0, -24.7],
  [126.0, -22.9], [131.0, -24.8], [136.0, -24.6], [140.0, -21.8], [143.0, -23.8],
  [146.0, -23.2], [151.0, -24.6], [154.0, -22.1], [157.0, -23.6], [160.0, -22.3],
  [164.0, -23.9], [167.0, -21.7], [171.0, -24.2], [173.5, -22.1], [176.0, -23.4],
  [180.0, -22.2], [180.0, -21.8], [179.0, -21.1], [176.0, -21.4], [171.0, -20.7],
  [166.0, -22.0], [161.0, -21.5], [156.0, -22.5], [151.0, -21.0], [146.0, -21.3],
  [141.0, -20.0], [136.0, -18.9], [131.0, -19.6], [126.0, -19.9], [121.0, -18.3],
  [116.0, -17.6], [111.0, -18.7], [106.0, -20.4], [101.0, -19.0], [96.0, -18.2],
  [91.0, -19.2], [86.0, -20.0], [81.0, -18.3], [76.0, -17.8], [71.0, -19.4],
  [66.0, -19.5], [61.0, -18.2], [56.0, -17.9], [51.0, -18.5], [46.0, -19.4],
  [41.0, -19.4], [36.0, -18.6], [31.0, -17.7], [26.0, -17.7], [21.0, -18.5],
  [16.0, -19.4], [11.0, -19.4], [6.0, -18.6], [1.0, -17.7], [-3.0, -18.3],
  [-7.0, -17.7], [-11.0, -19.4], [-14.0, -17.7], [-3.0, -8.5], [4.0, -8.9],
  [3.0, -13.1], [5.0, -6.5], [9.5, -0.3], [9.4, 0.3], [9.3, 1.0],
  [10.0, 2.0], [10.2, 3.2], [8.1, 4.6], [5.0, 6.2], [2.7, 5.5],
  [-0.3, 5.6], [-2.8, 4.9], [-5.5, 5.5], [-7.6, 6.4], [-10.0, 7.2],
  [-13.5, 8.2], [-16.2, 8.3], [-16.0, 9.6], [-13.0, 10.0], [-14.0, 12.7],
  [-15.5, 12.4], [-16.7, 13.3], [-17.2, 19.5], [-16.0, 24.1], [-13.3, 27.2],
  [-9.3, 28.9], [-9.8, 30.3], [-8.1, 31.4], [-6.9, 32.3], [-6.3, 33.2],
  [-6.0, 34.2], [-5.9, 35.8]
];

function proj(lng: number, lat: number): [number, number] {
  const x = ((lng + 25) / 110) * W * 0.5 + W * 0.24;
  const y = ((37 - lat) / 75) * H * 0.62 + H * 0.1;
  return [x, y];
}

export default function CoverageSection({ text }: { text: CoverageText }) {
  const pathD = COAST.map(([lng, lat], i) => {
    const [x, y] = proj(lng, lat);
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");

  return (
    <section id="coverage" className="relative z-10 bg-mineral/90 text-graphite py-24 px-6 sm:px-10 lg:px-14">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-5">
          <RevealOnScroll>
            <span className="mono-label text-signal inline-flex items-center gap-3">
              <span className="w-8 h-px bg-signal" />
              {text.eyebrow}
            </span>
            <h2 className="font-display font-bold text-4xl sm:text-5xl tracking-tight mt-5">
              {text.title}
            </h2>
            <p className="mt-5 text-steel leading-relaxed max-w-md">{text.subtitle}</p>
          </RevealOnScroll>

          <RevealOnScroll delay={150}>
            <div className="mt-10 grid grid-cols-1 gap-px bg-mineral-3 border border-mineral-3 max-w-md">
              <div className="bg-white px-6 py-4 flex items-baseline justify-between">
                <span className="mono-label text-steel">{text.bandLabel}</span>
                <span className="font-mono text-sm font-semibold"><CountUp value={text.bandValue} /></span>
              </div>
              <div className="bg-white px-6 py-4 flex items-baseline justify-between">
                <span className="mono-label text-steel">{text.backhaulLabel}</span>
                <span className="font-mono text-sm font-semibold"><CountUp value={text.backhaulValue} /></span>
              </div>
              <div className="bg-white px-6 py-4 flex items-baseline justify-between">
                <span className="mono-label text-steel">{text.elevationLabel}</span>
                <span className="font-mono text-sm font-semibold"><CountUp value={text.elevationValue} /></span>
              </div>
            </div>
            <p className="mono-label text-steel mt-6">{text.simulationLabel}</p>
          </RevealOnScroll>
        </div>

        <RevealOnScroll delay={200} className="lg:col-span-7">
          <div className="grid-paper border border-mineral-3 p-6 sm:p-10">
            <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto" role="img" aria-label="Pan-African ground station coverage">
              <path d={pathD} fill="none" stroke="#15171A" strokeWidth="2.5" strokeLinejoin="round" />
              {STATIONS.map((s) => {
                const [x, y] = proj(s.lng, s.lat);
                return (
                  <g key={s.id}>
                    <circle
                      className="animate-radar-ping"
                      cx={x}
                      cy={y}
                      r="10"
                      fill="none"
                      stroke="#E2662F"
                      strokeWidth="1"
                    />
                    <circle
                      className="animate-beam"
                      cx={x}
                      cy={y}
                      r="10"
                      fill="none"
                      stroke="#E2662F"
                      strokeWidth="1"
                      opacity="0.5"
                    />
                    <circle cx={x} cy={y} r="4.5" fill="#E2662F" />
                    <text x={x + 12} y={y + 4} fontSize="12" fontFamily="monospace" fill="#6D737C">
                      {s.name.split(" ")[0].toUpperCase()}
                    </text>
                  </g>
                );
              })}
              {/* Backhaul lines to a central network node */}
              {STATIONS.map((s) => {
                const [x, y] = proj(s.lng, s.lat);
                return (
                  <line
                    key={`line-${s.id}`}
                    className="animate-trace"
                    x1={x}
                    y1={y}
                    x2={W / 2}
                    y2={H * 0.5}
                    stroke="#5C7D62"
                    strokeWidth="1"
                    strokeDasharray="4 5"
                    opacity="0.55"
                  />
                );
              })}
              <circle cx={W / 2} cy={H * 0.5} r="7" fill="#5C7D62" />
              <text
                x={W / 2}
                y={H * 0.5 - 14}
                textAnchor="middle"
                fontSize="12"
                fontFamily="monospace"
                fill="#5C7D62"
              >
                AFRI-GROUND NETWORK
              </text>
            </svg>
          </div>
        </RevealOnScroll>
      </div>
    </section>
  );
}