import { ModuleCard } from "./ModuleCard";
import type { TelemetrySnapshot } from "../lib/types";

export function SettingsPanel({ data }: { data: TelemetrySnapshot }) {
  return (
    <ModuleCard title="Settings">
      <div className="space-y-2 text-xs">
        <div className="rounded bg-slate-800 p-2">
          <div className="text-slate-400">Trading Mode</div>
          <div>{data.mode.toUpperCase()}</div>
        </div>
        <div className="rounded bg-slate-800 p-2">
          <div className="text-slate-400">Symbols Scope</div>
          <div>NIFTY, SENSEX</div>
        </div>
        <div className="rounded bg-slate-800 p-2">
          <div className="text-slate-400">Safety Rule</div>
          <div>Upstox + MarketDataStreamerV3 required</div>
        </div>
      </div>
    </ModuleCard>
  );
}
