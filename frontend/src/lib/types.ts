export type BrokerState = {
  broker_connected: boolean;
  market_stream_connected: boolean;
  safe_mode: boolean;
  reason: string;
  execution_latency_ms: number;
  slippage_bps: number;
};

export type OrderFlowSnapshot = {
  cumulative_delta: number;
  delta_velocity: number;
  dom_imbalance: number;
  aggressive_buyers: number;
  breakout_acceleration: number;
};

export type HeatmapSnapshot = {
  liquidity_walls: number[];
  stop_loss_clusters: number[];
  gamma_zones: number[];
  bid_absorption: number;
  liquidity_voids: number[];
  sweep_zones: number[];
};

export type TradeSignal = {
  symbol: "NIFTY" | "SENSEX";
  direction: "BUY" | "SELL";
  score: number;
  rationale: string[];
  confidence: number;
  target_points: number;
  stop_points: number;
};

export type Position = {
  symbol: string;
  qty: number;
  avg_price: number;
  ltp: number;
  unrealized_pnl: number;
  realized_pnl: number;
};

export type TelemetrySnapshot = {
  ts: string;
  broker: BrokerState;
  available_capital: number;
  used_margin: number;
  realized_pnl: number;
  unrealized_pnl: number;
  active_positions: Position[];
  open_orders: Record<string, unknown>[];
  exposure_pct: number;
  mode: "simulator" | "paper" | "live";
  stale_feed: boolean;
  tqs: number;
  heuristic_tqs: number;
  model_probability: number | null;
  ai_model_ready: boolean;
  ai_model_version: string | null;
  signal: TradeSignal | null;
  safe_mode_reason: string;
  heatmap: HeatmapSnapshot;
  orderflow: OrderFlowSnapshot;
};
