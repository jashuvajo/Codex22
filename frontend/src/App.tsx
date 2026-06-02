import { AIMatrix } from "./components/AIMatrix";
import { ExecutionHUD } from "./components/ExecutionHUD";
import { HeatmapTerminal } from "./components/HeatmapTerminal";
import { OrderflowAnalytics } from "./components/OrderflowAnalytics";
import { RiskEnginePanel } from "./components/RiskEnginePanel";
import { SessionIntelligence } from "./components/SessionIntelligence";
import { SettingsPanel } from "./components/SettingsPanel";
import { TradeJournalPanel } from "./components/TradeJournalPanel";
import { UpstoxPortfolio } from "./components/UpstoxPortfolio";
import { useTelemetry } from "./hooks/useTelemetry";

export default function App() {
  const { snapshot, connected } = useTelemetry();

  return (
    <main className="min-h-screen bg-terminal-bg px-4 py-4 text-slate-100">
      <header className="mb-4 flex items-center justify-between rounded border border-slate-700 bg-terminal-panel p-3 shadow-bloomberg">
        <div>
          <h1 className="text-xl font-bold tracking-wide text-terminal-accent">NEXUSQUANT</h1>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Minimal Institutional AI Scalping Terminal Prompt</p>
        </div>
        <div className="text-right text-xs">
          <div>Universe: NIFTY / SENSEX</div>
          <div className={snapshot.broker.safe_mode ? "text-terminal-warning" : "text-terminal-success"}>
            {snapshot.broker.safe_mode ? "SAFE MODE" : "EXECUTION ENABLED"}
          </div>
        </div>
      </header>

      <section className="grid grid-cols-1 gap-3 xl:grid-cols-4">
        <ExecutionHUD data={snapshot} wsConnected={connected} />
        <AIMatrix tqs={snapshot.tqs} signal={snapshot.signal} />
        <OrderflowAnalytics flow={snapshot.orderflow} />
        <HeatmapTerminal heatmap={snapshot.heatmap} />
        <UpstoxPortfolio data={snapshot} />
        <RiskEnginePanel data={snapshot} />
        <TradeJournalPanel data={snapshot} />
        <SessionIntelligence data={snapshot} />
        <SettingsPanel data={snapshot} />
      </section>
    </main>
  );
}
