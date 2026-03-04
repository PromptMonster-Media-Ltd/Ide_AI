# Ide/AI — Railway Deployment Guide

Step-by-step guide to deploy Ide/AI (React frontend + FastAPI backend + PostgreSQL) on [Railway](https://railway.com).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Railway Project                       │
│                                                         │
│  ┌─────────────────┐   Public domain (your-app.up.railway.app)
│  │  Caddy Reverse   │◄──── Only public-facing service   │
│  │  Proxy           │                                   │
│  └───┬─────────┬───┘                                   │
│      │ /api/*  │  /*        Private IPv6 network        │
│      ▼         ▼                                        │
│  ┌────────┐  ┌──────────┐  ┌────────────┐              │
│  │Backend │  │ Frontend │  │ PostgreSQL │              │
│  │FastAPI │  │ Vite+    │  │            │              │
│  │        │←─┤ Caddy    │  │            │              │
│  │        │──┼──────────┼─►│            │              │
│  └────────┘  └──────────┘  └────────────┘              │
│   /backend     /frontend     (managed DB)               │
└─────────────────────────────────────────────────────────┘
```

**4 services total:**
1. **PostgreSQL** — Managed database (one-click provision)
2. **Backend** — FastAPI + Uvicorn (from `/backend`)
3. **Frontend** — Static Vite build served by Caddy (from `/frontend`)
4. **Caddy Proxy** — Reverse proxy, single public domain (from `/railway`)

---

## Prerequisites

- A [Railway account](https://railway.com) (free Hobby tier works to start)
- Your code pushed to a **GitHub repository**
- Your **Anthropic API key** (`sk-ant-...`)

---

## Step 1 — Create the Railway Project

1. Go to [railway.com/dashboard](https://railway.com/dashboard)
2. Click **"+ New Project"** → **"Empty Project"**
3. Name it `ide-ai` (or whatever you prefer)

---

## Step 2 — Provision PostgreSQL

1. Inside your project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway instantly provisions a Postgres 15 instance
3. Click the Postgres service → **"Variables"** tab
4. Note that `DATABASE_URL` is automatically generated — you'll reference this later

> **Tip:** The `DATABASE_URL` variable points to the *private* internal URL by default. This is exactly what you want — internal traffic is faster and free.

---

## Step 3 — Deploy the Backend

1. In your project, click **"+ New"** → **"GitHub Repo"**
2. Select your Ide/AI repository
3. Railway will create a new service. Go to **Settings**:

| Setting | Value |
|---------|-------|
| **Root Directory** | `/backend` |
| **Config File Path** | `/backend/railway.toml` |
| **Watch Paths** | `/backend/**` |

4. Go to the **Variables** tab and add:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `SECRET_KEY` | *(click "Generate" for a random 64-char string)* |
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` *(your key)* |
| `ENVIRONMENT` | `production` |

> **Important:** Use the Railway variable reference syntax `${{Postgres.DATABASE_URL}}` — this automatically resolves to the private internal URL.

> **About `DATABASE_URL` format:** Railway provides a `postgresql://...` URL. If asyncpg complains, you may need to replace `postgresql://` with `postgresql+asyncpg://`. You can do this with a Railway variable transform: set `DATABASE_URL` to `${{Postgres.DATABASE_URL}}` and then create a second variable like `SQLALCHEMY_DATABASE_URL` that patches the scheme. Alternatively, handle it in your `config.py`.

5. Click **"Deploy"** — Railway will:
   - Build the Docker image (from `backend/Dockerfile`)
   - Run `alembic upgrade head` (pre-deploy command creates tables)
   - Start Uvicorn on `[::]:$PORT`

6. Verify: once deployed, check the deploy logs for:
   ```
   INFO:     Uvicorn running on http://[::]:8000
   ```

---

## Step 4 — Deploy the Frontend

1. Click **"+ New"** → **"GitHub Repo"** → select the **same repo** again
2. Go to **Settings**:

| Setting | Value |
|---------|-------|
| **Root Directory** | `/frontend` |
| **Config File Path** | `/frontend/railway.toml` |
| **Watch Paths** | `/frontend/**` |

3. Go to **Variables** and add:

| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | `/api/v1` |
| `PORT` | `3000` |

> **Note:** `VITE_API_BASE_URL=/api/v1` works because the Caddy reverse proxy (next step) routes `/api/*` to the backend. The value is baked into the JS bundle at build time.

4. Click **"Deploy"**

---

## Step 5 — Deploy the Caddy Reverse Proxy

This service gives you a **single public domain** for the entire app. No CORS issues.

1. Click **"+ New"** → **"GitHub Repo"** → select the **same repo** again
2. Go to **Settings**:

| Setting | Value |
|---------|-------|
| **Root Directory** | `/railway` |
| **Watch Paths** | `/railway/**` |

3. Go to **Variables** and add:

| Variable | Value |
|----------|-------|
| `FRONTEND_DOMAIN` | `${{Frontend.RAILWAY_PRIVATE_DOMAIN}}` |
| `FRONTEND_PORT` | `${{Frontend.PORT}}` |
| `BACKEND_DOMAIN` | `${{Backend.RAILWAY_PRIVATE_DOMAIN}}` |
| `BACKEND_PORT` | `${{Backend.PORT}}` |

> **Note:** Replace `Frontend` and `Backend` with the actual service names you see in Railway if you renamed them.

4. Go to **Settings** → **Networking** → **"Generate Domain"**
   - This gives you a public URL like `ide-ai-production.up.railway.app`
   - **Only attach a public domain to this Caddy proxy service** — not to backend or frontend

5. Click **"Deploy"**

---

## Step 6 — Verify the Deployment

1. Open your public URL: `https://your-app.up.railway.app`
2. You should see the Ide/AI home page with the nebula canvas
3. Test the API health endpoint: `https://your-app.up.railway.app/api/v1/health`
   - Should return `{"status": "ok"}`
4. Try creating a project and starting a Discovery session

---

## Step 7 — Custom Domain (Optional)

1. Click the **Caddy Proxy** service → **Settings** → **Networking**
2. Click **"+ Custom Domain"**
3. Enter your domain (e.g., `app.ide-ai.dev`)
4. Add the CNAME record shown to your DNS provider
5. Railway auto-provisions an SSL certificate via Let's Encrypt

---

## Environment Variables Reference

### Backend Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string (use `${{Postgres.DATABASE_URL}}`) |
| `SECRET_KEY` | Yes | — | JWT signing secret (min 32 chars) |
| `ANTHROPIC_API_KEY` | Yes | — | Claude API key for AI features |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Not needed with Caddy proxy (same-origin). Only set if backend is exposed directly. |
| `ENVIRONMENT` | No | `development` | `production` or `development` |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-6` | Anthropic model to use |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` | JWT token lifetime (7 days) |

### Frontend Service

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `/api/v1` | API base URL (baked at build time) |
| `PORT` | No | `3000` | Port for Caddy to listen on |

### Caddy Proxy Service

| Variable | Required | Description |
|----------|----------|-------------|
| `FRONTEND_DOMAIN` | Yes | `${{Frontend.RAILWAY_PRIVATE_DOMAIN}}` |
| `FRONTEND_PORT` | Yes | `${{Frontend.PORT}}` |
| `BACKEND_DOMAIN` | Yes | `${{Backend.RAILWAY_PRIVATE_DOMAIN}}` |
| `BACKEND_PORT` | Yes | `${{Backend.PORT}}` |

---

## Handling Database Migrations

Migrations run **automatically** on every deploy via `railway.toml`:

```toml
[deploy]
preDeployCommand = "alembic upgrade head"
```

This runs **after** the Docker image builds but **before** the new container replaces the old one. If the migration fails, the deploy is rolled back — your existing version keeps running.

### Creating new migrations locally

```bash
cd backend
python -m poetry run alembic revision --autogenerate -m "add_new_table"
```

Commit the migration file, push to GitHub, and Railway will apply it on the next deploy.

---

## Troubleshooting

### Backend can't connect to Postgres

- Make sure `DATABASE_URL` uses `${{Postgres.DATABASE_URL}}` (reference syntax, not a hardcoded URL)
- Railway's private network is IPv6-only — if you see connection errors, ensure your code doesn't force IPv4
- The private network is NOT available during `buildCommand` — migrations must use `preDeployCommand`

### Frontend shows blank page

- Check that `VITE_API_BASE_URL` is set as a **build-time** variable (it's baked into the JS bundle)
- Make sure the Caddyfile has `try_files {path} /index.html` for SPA routing

### API returns CORS errors

- If using the Caddy proxy (recommended), you shouldn't see CORS errors since everything is same-origin
- If you see CORS errors, check `CORS_ORIGINS` on the backend matches your public domain exactly (including `https://`)

### Deploy fails at migration step

- Check the deploy logs — the `preDeployCommand` output is shown
- Common issue: `DATABASE_URL` scheme mismatch. Railway gives `postgresql://`, but asyncpg may need `postgresql+asyncpg://`. Fix in `config.py`:
  ```python
  @property
  def async_database_url(self) -> str:
      return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
  ```

### Build takes too long

- Docker layer caching: `pyproject.toml` and `package.json` are copied before source code, so dependency installs are cached across deploys
- If builds are still slow, consider using Railway's build caching features

---

## Cost Estimate

Railway Hobby plan ($5/month base):
- **PostgreSQL**: ~$0.000231/hr (~$0.17/month idle)
- **Backend**: ~$0.000463/hr (512MB RAM)
- **Frontend**: ~$0.000231/hr (static serving is lightweight)
- **Caddy Proxy**: ~$0.000115/hr (minimal resources)

**Estimated total: ~$7-12/month** with light usage. Scales with traffic.

---

## Files Created for Railway

```
Ide_AI/
├── backend/
│   ├── Dockerfile         ← Multi-stage production build
│   └── railway.toml       ← Build + deploy config
├── frontend/
│   ├── Dockerfile         ← Multi-stage build → Caddy static server
│   ├── Caddyfile          ← SPA routing + caching headers
│   └── railway.toml       ← Build + deploy config
└── railway/
    ├── Dockerfile         ← Caddy reverse proxy image
    └── Caddyfile          ← Routes /api/* → backend, /* → frontend
```
