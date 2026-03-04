# ────────────────────────────────────────────────────────────────
# Ide/AI Frontend — Production Dockerfile (Railway-ready)
# Multi-stage build: npm build → Caddy static server
# ────────────────────────────────────────────────────────────────

# ── Stage 1: Build static assets ──
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# VITE_API_BASE_URL is baked in at build time.
# When using Caddy reverse proxy (recommended), set to /api/v1
# When using direct cross-origin, set to https://your-backend.up.railway.app/api/v1
ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ── Stage 2: Serve with Caddy ──
FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /app/dist /srv

# Railway injects $PORT at runtime
ENV PORT=3000
