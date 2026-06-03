import { ModuleCard } from "./ModuleCard";
import type { OrderFlowSnapshot } from "../lib/types";

export function OrderflowAnalytics({ flow }: { flow: OrderFlowSnapshot }) {
  return (
    <ModuleCard title="Orderflow Analytics">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">Cumulative Delta</div>
          <div className="mt-1 text-base text-terminal-accent">{flow.cumulative_delta.toFixed(2)}</div>
        </div>
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">Delta Velocity</div>
          <div className="mt-1 text-base text-slate-50">{flow.delta_velocity.toFixed(4)}</div>
        </div>
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">DOM Imbalance</div>
          <div className="mt-1 text-base text-slate-50">{flow.dom_imbalance.toFixed(4)}</div>
        </div>
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">Aggressive Buyers</div>
          <div className="mt-1 text-base text-terminal-success">{(flow.aggressive_buyers * 100).toFixed(1)}%</div>
        </div>
      </div>
      <div className="mt-3 text-xs text-slate-400">Breakout Acceleration: {flow.breakout_acceleration.toFixed(2)}</div>
    </ModuleCard>
  );
}
