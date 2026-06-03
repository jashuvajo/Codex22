import { ModuleCard } from "./ModuleCard";
import type { TradeSignal } from "../lib/types";

type AIMatrixProps = {
  tqs: number;
  heuristicTqs: number;
  modelProbability: number | null;
  modelReady: boolean;
  modelVersion: string | null;
  signal: TradeSignal | null;
};

export function AIMatrix({
  tqs,
  heuristicTqs,
  modelProbability,
  modelReady,
  modelVersion,
  signal
}: AIMatrixProps) {
  return (
    <ModuleCard title="AI Matrix">
      <div className="space-y-2 text-xs">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Fused Trade Quality Score</span>
          <span className="text-lg font-semibold text-terminal-accent">{tqs.toFixed(2)}</span>
        </div>
        <div className="h-2 overflow-hidden rounded bg-slate-800">
          <div className="h-full bg-terminal-accent transition-all" style={{ width: `${Math.min(tqs, 100)}%` }} />
        </div>

        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="rounded bg-slate-800/70 p-2">
            <div className="text-slate-400">Heuristic TQS</div>
            <div>{heuristicTqs.toFixed(2)}</div>
          </div>
          <div className="rounded bg-slate-800/70 p-2">
            <div className="text-slate-400">Model Probability</div>
            <div>{modelProbability == null ? "N/A" : `${(modelProbability * 100).toFixed(1)}%`}</div>
          </div>
        </div>

        <div className="rounded border border-slate-700 bg-slate-800/60 p-2 text-[11px] text-slate-300">
          Model: {modelReady ? "READY" : "NOT TRAINED"}
          {modelVersion ? ` (${modelVersion})` : ""}
        </div>

        {signal ? (
          <div className="rounded border border-terminal-success/20 bg-terminal-success/10 p-2 text-terminal-success">
            <div className="font-semibold">
              {signal.symbol} {signal.direction} ({(signal.confidence * 100).toFixed(1)}%)
            </div>
            <ul className="ml-4 mt-1 list-disc space-y-0.5 text-[11px]">
              {signal.rationale.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="rounded border border-slate-700 bg-slate-800/60 p-2 text-slate-400">
            No active signal. Scanning momentum every second.
          </div>
        )}
      </div>
    </ModuleCard>
  );
}
