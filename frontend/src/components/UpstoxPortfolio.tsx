import { ModuleCard } from "./ModuleCard";
import type { Position, TelemetrySnapshot } from "../lib/types";

function PositionRow({ position }: { position: Position }) {
  const pnlColor = position.unrealized_pnl >= 0 ? "text-terminal-success" : "text-terminal-danger";
  return (
    <tr className="border-b border-slate-800 text-xs">
      <td className="py-1">{position.symbol}</td>
      <td>{position.qty}</td>
      <td>{position.avg_price.toFixed(2)}</td>
      <td>{position.ltp.toFixed(2)}</td>
      <td className={pnlColor}>{position.unrealized_pnl.toFixed(2)}</td>
    </tr>
  );
}

export function UpstoxPortfolio({ data }: { data: TelemetrySnapshot }) {
  return (
    <ModuleCard title="Upstox Portfolio">
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">Available Capital</div>
          <div className="text-terminal-accent">{data.available_capital.toFixed(2)}</div>
        </div>
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">Used Margin</div>
          <div>{data.used_margin.toFixed(2)}</div>
        </div>
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">Realized PnL</div>
          <div>{data.realized_pnl.toFixed(2)}</div>
        </div>
        <div className="rounded bg-slate-800/70 p-2">
          <div className="text-slate-400">Unrealized PnL</div>
          <div>{data.unrealized_pnl.toFixed(2)}</div>
        </div>
      </div>
      <table className="mt-3 w-full text-left text-xs text-slate-200">
        <thead className="text-[11px] uppercase tracking-wide text-slate-400">
          <tr>
            <th>Symbol</th>
            <th>Qty</th>
            <th>Avg</th>
            <th>LTP</th>
            <th>uPnL</th>
          </tr>
        </thead>
        <tbody>
          {data.active_positions.length ? (
            data.active_positions.map((p) => <PositionRow position={p} key={`${p.symbol}-${p.qty}-${p.avg_price}`} />)
          ) : (
            <tr>
              <td colSpan={5} className="py-2 text-slate-500">
                No active positions
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </ModuleCard>
  );
}
