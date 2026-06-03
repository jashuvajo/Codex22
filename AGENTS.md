# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

NexusQuant is an AI scalping terminal (FastAPI backend + React/Vite frontend). Local dev needs **PostgreSQL 16**, **Redis 7**, the **backend** API on port **8000**, and the **frontend** on port **5173**. See `README.md` for architecture and API list.

### System dependencies (one-time on the VM)

Docker is **not** required for local dev if Postgres and Redis run on the host:

```bash
sudo apt-get install -y postgresql redis-server python3.12-venv
sudo service postgresql start
sudo service redis-server start
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
sudo -u postgres createdb nexusquant  # ignore error if DB already exists
```

Alternatively, use the full stack via `docker compose up --build` from the repo root (requires Docker).

### Environment files

Copy templates once (not in git):

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

For **host-based** dev (no Docker Compose network), set in `backend/.env`:

- `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/nexusquant`
- `REDIS_URL=redis://localhost:6379/0`
- `REQUIRE_LIVE_UPSTOX_CONNECTION=false` — uses the built-in simulator stream without Upstox tokens (SAFE MODE remains on until Upstox REST credentials are provided).

### Starting services

Use **tmux** for long-running processes. Example:

```bash
# Backend (from repo root)
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run dev -- --host 0.0.0.0 --port 5173
```

Verify: `curl http://localhost:8000/health` and open `http://localhost:5173`.

### Lint / test / build

| Area | Command | Notes |
|------|---------|--------|
| Backend tests | `cd backend && PYTHONPATH=. .venv/bin/pytest tests/ -q` | `pytest` is not in `requirements.txt`; install in the venv if missing. |
| Frontend build | `cd frontend && npm run build` | Runs `tsc -b` + Vite production build. |
| Backend lint | — | No ESLint/ruff/mypy config in repo. |
| Frontend lint | — | No ESLint script in `package.json`. |

### Gotchas

- **pytest import errors**: run tests with `PYTHONPATH=.` from `backend/`.
- **venv creation fails** on Ubuntu: install `python3.12-venv` before `python3 -m venv .venv`.
- **EXECUTION ENABLED** in production requires valid `UPSTOX_API_KEY` / `UPSTOX_ACCESS_TOKEN` and `REQUIRE_LIVE_UPSTOX_CONNECTION=true`; local demo typically runs in simulator + SAFE MODE with broker disconnected.
- **Postgres/Redis hostnames** in `.env.example` (`postgres`, `redis`) are for Docker Compose only; use `localhost` when running services on the VM host.
