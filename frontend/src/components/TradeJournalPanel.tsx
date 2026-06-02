import { ModuleCard } from "./ModuleCard";
import type { TelemetrySnapshot } from "../lib/types";

export function TradeJournalPanel({ data }: { data: TelemetrySnapshot }) {
  return (
    <ModuleCard title="Trade Journal">
      {data.signal ? (
        <div className="space-y-2 text-xs">
          <div className="rounded bg-slate-800 p-2">
            <div className="text-slate-400">Latest Signal</div>
            <div className="text-terminal-accent">
              {data.signal.symbol} {data.signal.direction} @ score {data.signal.score.toFixed(2)}
            </div>
          </div>
          <div className="rounded bg-slate-800 p-2">
            <div className="text-slate-400">Target / Stop</div>
            <div>
              +{data.signal.target_points} / -{data.signal.stop_points}
            </div>
          </div>
        </div>
      ) : (
        <p className="text-xs text-slate-500">No trade journal events yet. Waiting for validated TQS signals.</p>
      )}
    </ModuleCard>
  );
}
