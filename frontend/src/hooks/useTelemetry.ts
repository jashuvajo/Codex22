import { useEffect, useMemo, useState } from "react";
import type { TelemetrySnapshot } from "../lib/types";

const initialState: TelemetrySnapshot = {
  ts: new Date().toISOString(),
  broker: {
    broker_connected: false,
    market_stream_connected: false,
    safe_mode: true,
    reason: "Waiting for broker connection",
    execution_latency_ms: 0,
    slippage_bps: 0
  },
  available_capital: 0,
  used_margin: 0,
  realized_pnl: 0,
  unrealized_pnl: 0,
  active_positions: [],
  open_orders: [],
  exposure_pct: 0,
  mode: "simulator",
  stale_feed: true,
  tqs: 0,
  heuristic_tqs: 0,
  model_probability: null,
  ai_model_ready: false,
  ai_model_version: null,
  signal: null,
  safe_mode_reason: "SAFE MODE",
  heatmap: {
    liquidity_walls: [],
    stop_loss_clusters: [],
    gamma_zones: [],
    bid_absorption: 0,
    liquidity_voids: [],
    sweep_zones: []
  },
  orderflow: {
    cumulative_delta: 0,
    delta_velocity: 0,
    dom_imbalance: 0,
    aggressive_buyers: 0,
    breakout_acceleration: 0
  }
};

export function useTelemetry() {
  const [snapshot, setSnapshot] = useState<TelemetrySnapshot>(initialState);
  const [connected, setConnected] = useState(false);

  const wsUrl = useMemo(
    () => import.meta.env.VITE_TELEMETRY_WS_URL ?? "ws://localhost:8000/ws/telemetry",
    []
  );

  useEffect(() => {
    const ws = new WebSocket(wsUrl);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (event: MessageEvent<string>) => {
      try {
        const parsed = JSON.parse(event.data) as TelemetrySnapshot;
        setSnapshot(parsed);
      } catch {
        // Ignore malformed payloads.
      }
    };
    const heartbeat = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 3000);

    return () => {
      clearInterval(heartbeat);
      ws.close();
    };
  }, [wsUrl]);

  return { snapshot, connected };
}
