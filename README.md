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


## Real-time Upstox Data Collection & AI Training

Yes, real-time data collection is supported. NexusQuant now persists every analyzed market snapshot into PostgreSQL (`market_feature_snapshots`) while feed is live.

Training flow:

1. Collect tick/orderflow/heatmap features each second.
2. Label samples by checking whether premium expands by `AI_TARGET_POINTS` within `AI_LABEL_LOOKAHEAD_SECONDS`.
3. Train supervised model (RandomForest) from feature store.
4. Save and load model via local registry artifact path (`AI_MODEL_PATH`).
5. Fuse model probability with heuristic TQS for higher quality scalp decisions.

New API endpoints:

- `GET /api/v1/ai/status`
- `POST /api/v1/ai/train`

Model status is streamed in telemetry (`ai_model_ready`, `ai_model_version`, `model_probability`, `heuristic_tqs`).



## AWS Production Deployment (Recommended)

Target architecture:

- Vercel frontend (`app.nexusquant.ai`)
- AWS ALB (`api.nexusquant.ai`) with HTTPS + WSS
- ECS Fargate backend (FastAPI)
- RDS PostgreSQL (private subnets)
- ElastiCache Redis (private subnets)
- Secrets Manager for credentials/tokens
- CloudWatch logs + alarms + ECS autoscaling

Terraform folder layout:

```text
infra/aws/
├── main.tf
├── variables.tf
├── outputs.tf
├── networking.tf
├── alb.tf
├── ecs.tf
├── rds.tf
├── redis.tf
├── iam.tf
├── secrets.tf
├── cloudwatch.tf
└── terraform.tfvars.example
```

### Quick deploy flow

1. Copy and fill variables:

```bash
cd infra/aws
cp terraform.tfvars.example terraform.tfvars
# edit values: backend_image, acm_certificate_arn, Route53, Upstox creds
```

2. Build and push backend image:

```bash
docker build --platform linux/amd64 -t nexusquant-backend ./backend
```

3. Apply Terraform:

```bash
terraform init
terraform plan
terraform apply
```

4. Point frontend telemetry URL:

```bash
VITE_API_BASE_URL=https://api.nexusquant.ai
VITE_TELEMETRY_WS_URL=wss://api.nexusquant.ai/ws/telemetry
```

### One-command script

You can run:

```bash
./scripts/deploy_aws.sh ap-south-1 <ACCOUNT_ID> <ACM_CERTIFICATE_ARN>
```

### Runtime defaults baked into ECS task

- `TRADING_MODE=simulator`
- `REQUIRE_LIVE_UPSTOX_CONNECTION=true`
- `UPSTOX_BASE_URL=https://api.upstox.com/v2`
- `UPSTOX_MARKET_AUTHORIZE_ENDPOINT=/v3/feed/market-data-feed/authorize`
- `WS_HEARTBEAT_INTERVAL=15`
- `REDIS_CHANNEL=market_ticks`

### Operational safeguards included

- ALB idle timeout set to `300` for websocket stability
- ECS target group health check at `/health`
- ECS autoscaling (`min=1`, `max=4`) on CPU + memory
- CloudWatch alarms for CPU, memory, and low running task count
- private subnets for ECS/RDS/Redis with NAT egress for broker/API access
