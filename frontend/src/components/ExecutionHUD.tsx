import { ModuleCard } from "./ModuleCard";
import type { TelemetrySnapshot } from "../lib/types";

function statLabel(label: string, value: string, danger?: boolean) {
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-slate-400">{label}</span>
      <span className={danger ? "font-medium text-terminal-danger" : "font-medium text-slate-100"}>{value}</span>
    </div>
  );
}

export function ExecutionHUD({ data, wsConnected }: { data: TelemetrySnapshot; wsConnected: boolean }) {
  const brokerHealthy = data.broker.broker_connected && data.broker.market_stream_connected && !data.stale_feed;
  const statusColor = brokerHealthy ? "text-terminal-success" : "text-terminal-danger";

  return (
    <ModuleCard
      title="Execution HUD"
      rightSlot={<span className={`text-xs font-bold ${statusColor}`}>{brokerHealthy ? "CONNECTED" : "DISCONNECTED"}</span>}
    >
      <div className="space-y-2">
        {statLabel("WS Link", wsConnected ? "LIVE" : "DOWN", !wsConnected)}
        {statLabel("Broker Health", brokerHealthy ? "Healthy" : "Disconnected", !brokerHealthy)}
        {statLabel("Mode", data.mode.toUpperCase())}
        {statLabel("Trade Quality Score", data.tqs.toFixed(2))}
        {statLabel("Execution Latency", `${data.broker.execution_latency_ms.toFixed(1)} ms`, data.broker.execution_latency_ms > 250)}
        {statLabel("Slippage", `${data.broker.slippage_bps.toFixed(2)} bps`, data.broker.slippage_bps > 20)}
        {statLabel("Exposure", `${data.exposure_pct.toFixed(2)}%`, data.exposure_pct >= 40)}
      </div>
      {data.broker.safe_mode && (
        <div className="mt-3 rounded border border-terminal-warning/30 bg-terminal-warning/10 p-2 text-xs text-terminal-warning">
          SAFE MODE: {data.safe_mode_reason}
        </div>
      )}
    </ModuleCard>
  );
}
