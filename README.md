# NexusQuant - Minimal Institutional AI Scalping Terminal

NexusQuant is a professional AI-powered scalping platform focused on:

- **NIFTY**
- **SENSEX**

Tech stack:

- **Frontend:** React + Tailwind (Vite)
- **Backend:** FastAPI + asyncio + WebSockets
- **Broker:** Upstox APIs + MarketDataStreamerV3
- **Queue:** Redis
- **Database:** PostgreSQL
- **Monitoring:** Prometheus + Grafana

---

## Critical Safety Rule (implemented)

NexusQuant **must establish successful Upstox REST + MarketDataStreamerV3 connectivity first**.

If broker/feed is unavailable:

- trading is disabled,
- signal execution is disabled,
- broker shows disconnected,
- **SAFE MODE auto-activates**.

This gating is enforced in backend risk flow before strategy and execution routing.

---

## Project Structure

```text
backend/
  app/
    api/
    core/
    engines/
    services/
frontend/
  src/components/
infra/aws/
monitoring/prometheus/
docker-compose.yml
render.yaml
```

Core backend modules included:

- `ai_engine.py`
- `risk_engine.py`
- `trailing_engine.py`
- `heatmap_engine.py`
- `orderflow_engine.py`
- `strategy_router.py`
- `upstox_client.py`
- `execution_router.py`
- `analytics_engine.py`

Execution pipeline:

`Upstox Feed -> Telemetry -> Orderflow -> Heatmap -> AI Score -> Risk -> Strategy -> Execution -> Trailing -> Analytics`

---

## Modes

1. **Simulator mode** (`TRADING_MODE=simulator`) for dry-run flow
2. **Paper mode** (`TRADING_MODE=paper`) for non-live order simulation with live data
3. **Live mode** (`TRADING_MODE=live`) only after validation and controlled rollout

---

## Local Development

### 1) Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 3) Full stack with observability

```bash
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

---

## Deployment

### Frontend -> Vercel

- `frontend/vercel.json` is configured for Vite output.
- Set `VITE_TELEMETRY_WS_URL` to your backend WebSocket URL.

### Backend -> Render (initial)

- `render.yaml` includes backend web service, Postgres, and Redis references.
- Keep secrets in Render environment variables (never hardcoded).

### Backend -> AWS Mumbai (ap-south-1)

- Terraform baseline in `infra/aws` provisions ECS Fargate cluster/service and task definition.
- Use AWS Secrets Manager ARNs for:
  - Upstox API key
  - Upstox access token
  - Database URL
  - Redis URL

---

## API Endpoints

- `GET /health`
- `GET /metrics`
- `GET /api/v1/state`
- `POST /api/v1/risk/config`
- `POST /api/v1/trade/manual`
- `WS /ws/telemetry`

---

## Security Notes

- Never hardcode broker secrets.
- Use environment variables and secret managers only.
- Keep `REQUIRE_LIVE_UPSTOX_CONNECTION=true` in production to enforce connectivity-first behavior.
