import { ModuleCard } from "./ModuleCard";
import type { TelemetrySnapshot } from "../lib/types";

export function RiskEnginePanel({ data }: { data: TelemetrySnapshot }) {
  const safe = data.broker.safe_mode;
  return (
    <ModuleCard
      title="Risk Engine"
      rightSlot={<span className={`text-xs font-semibold ${safe ? "text-terminal-warning" : "text-terminal-success"}`}>{safe ? "SAFE MODE" : "ACTIVE"}</span>}
    >
      <ul className="space-y-2 text-xs">
        <li className="flex items-center justify-between">
          <span className="text-slate-400">Exposure %</span>
          <span className={data.exposure_pct > 40 ? "text-terminal-danger" : "text-slate-200"}>{data.exposure_pct.toFixed(2)}%</span>
        </li>
        <li className="flex items-center justify-between">
          <span className="text-slate-400">Feed Freshness</span>
          <span className={data.stale_feed ? "text-terminal-danger" : "text-terminal-success"}>{data.stale_feed ? "STALE" : "LIVE"}</span>
        </li>
        <li className="flex items-center justify-between">
          <span className="text-slate-400">Broker State</span>
          <span className={data.broker.broker_connected ? "text-terminal-success" : "text-terminal-danger"}>
            {data.broker.broker_connected ? "CONNECTED" : "DISCONNECTED"}
          </span>
        </li>
      </ul>
      <p className="mt-3 rounded border border-slate-700 bg-slate-800/80 p-2 text-xs text-slate-300">{data.safe_mode_reason}</p>
    </ModuleCard>
  );
}
