import { ModuleCard } from "./ModuleCard";
import type { HeatmapSnapshot } from "../lib/types";

function Row({ label, values }: { label: string; values: number[] }) {
  return (
    <div className="mb-2">
      <div className="text-[11px] uppercase tracking-wider text-slate-400">{label}</div>
      <div className="mt-1 flex flex-wrap gap-1">
        {values.length ? (
          values.map((v) => (
            <span key={`${label}-${v}`} className="rounded bg-slate-800 px-2 py-0.5 text-xs text-terminal-accent">
              {v.toFixed(2)}
            </span>
          ))
        ) : (
          <span className="text-xs text-slate-500">No zones</span>
        )}
      </div>
    </div>
  );
}

export function HeatmapTerminal({ heatmap }: { heatmap: HeatmapSnapshot }) {
  return (
    <ModuleCard title="Heatmap Terminal">
      <Row label="Liquidity Walls" values={heatmap.liquidity_walls} />
      <Row label="Stop-Loss Clusters" values={heatmap.stop_loss_clusters} />
      <Row label="Gamma Zones" values={heatmap.gamma_zones} />
      <Row label="Liquidity Voids" values={heatmap.liquidity_voids} />
      <Row label="Sweep Zones" values={heatmap.sweep_zones} />
      <div className="mt-2 text-xs text-slate-300">Bid Absorption: {(heatmap.bid_absorption * 100).toFixed(1)}%</div>
    </ModuleCard>
  );
}
