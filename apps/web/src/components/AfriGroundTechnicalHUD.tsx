"use client";

export type HudText = {
  networkLabel: string;
  stationLabel: string;
  stationId: string;
  position: string;
  rfLabel: string;
  rfValue: string;
  aosLabel: string;
  aosValue: string;
  losLabel: string;
  losValue: string;
  linkLabel: string;
  linkValue: string;
  liveLabel: string;
  simulLabel: string;
};

export default function AfriGroundTechnicalHUD({ text }: { text: HudText }) {
  return (
    <div className="console-panel border-t border-l border-r border-graphite-600/80 px-5 py-4">
      <div className="flex flex-wrap items-center gap-x-8 gap-y-3 font-mono text-[11px]">
        <div className="flex items-center gap-2.5">
          <span className="signal-indicator" />
          <span className="text-signal-soft font-semibold tracking-widest uppercase">
            {text.liveLabel}
          </span>
          <span className="px-1.5 py-0.5 text-[9px] text-steel border border-graphite-600 uppercase tracking-wider">
            {text.simulLabel}
          </span>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="text-graphite-mute uppercase">{text.stationLabel}</span>
          <span className="text-ink font-semibold">{text.stationId}</span>
          <span className="text-graphite-mute">{text.position}</span>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="text-graphite-mute uppercase">{text.rfLabel}</span>
          <span className="text-ink font-semibold">{text.rfValue}</span>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="text-graphite-mute uppercase">{text.aosLabel}</span>
          <span className="text-ink">{text.aosValue}</span>
          <span className="text-graphite-mute uppercase">{text.losLabel}</span>
          <span className="text-ink">{text.losValue}</span>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <span className="text-graphite-mute uppercase">{text.linkLabel}</span>
          <span className="text-green-soft font-semibold tracking-wider">
            {text.linkValue}
          </span>
        </div>
      </div>
    </div>
  );
}