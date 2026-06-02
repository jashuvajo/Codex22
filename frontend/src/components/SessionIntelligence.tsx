import { ModuleCard } from "./ModuleCard";
import type { TelemetrySnapshot } from "../lib/types";

export function SessionIntelligence({ data }: { data: TelemetrySnapshot }) {
  const regime = data.orderflow.breakout_acceleration > 0.8 ? "Momentum Expansion" : "Range / Choppy";
  const quality = data.tqs >= 70 ? "A-Grade Setup" : "Sub-threshold";

  return (
    <ModuleCard title="Session Intelligence">
      <div className="space-y-2 text-xs">
        <div className="rounded bg-slate-800 p-2">
          <div className="text-slate-400">Regime</div>
          <div>{regime}</div>
        </div>
        <div className="rounded bg-slate-800 p-2">
          <div className="text-slate-400">Current Quality</div>
          <div>{quality}</div>
        </div>
        <div className="rounded bg-slate-800 p-2">
          <div className="text-slate-400">Aggressive Buyers</div>
          <div>{(data.orderflow.aggressive_buyers * 100).toFixed(1)}%</div>
        </div>
      </div>
    </ModuleCard>
  );
}
