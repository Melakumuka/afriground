export type LiveNetwork = {
  missions: number;
  stations: number;
  datasets: number;
  slaViolations: number;
  rankedStations: number;
  outboxHealthy: boolean;
};

/**
 * Live-network status strip (Phase 4.2 visibility). Rendered only when the
 * backend API responded — otherwise it returns null so the landing never
 * claims a connection that does not exist.
 */
export default function LiveNetworkStrip({ network }: { network?: LiveNetwork }) {
  if (!network) return null;
  const items: { label: string; value: string }[] = [
    { label: "MISSIONS", value: String(network.missions) },
    { label: "STATIONS", value: String(network.stations) },
    { label: "DATASETS", value: String(network.datasets) },
    { label: "SLA VIOLATIONS", value: String(network.slaViolations) },
    { label: "RANKED STATIONS", value: String(network.rankedStations) },
    { label: "OUTBOX", value: network.outboxHealthy ? "HEALTHY" : "RETRYING" },
  ];
  return (
    <div className="relative z-10 bg-graphite/95 border-y border-graphite-600/60 text-ink">
      <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-14 py-3.5 flex flex-wrap items-center gap-x-8 gap-y-2">
        <span className="mono-label text-signal-soft inline-flex items-center gap-3">
          <span className="signal-indicator" />
          LIVE NETWORK
        </span>
        <span className="hidden lg:block w-px h-4 bg-graphite-600" />
        <div className="flex flex-wrap items-center gap-x-6 gap-y-1 font-mono text-[11px]">
          {items.map((it) => (
            <span key={it.label} className="inline-flex items-baseline gap-2">
              <span className="text-graphite-mute">{it.label}</span>
              <span className={it.label === "OUTBOX" && !network.outboxHealthy ? "text-signal-soft" : "text-white"}>
                {it.value}
              </span>
            </span>
          ))}
        </div>
        <span className="ml-auto mono-label text-green-soft inline-flex items-center gap-2">
          <span className="signal-indicator" />
          API CONNECTED
        </span>
      </div>
    </div>
  );
}