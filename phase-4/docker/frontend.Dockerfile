# Phase IV: Frontend Multi-Stage Docker Build (Next.js Standalone)
# Build context: phase-2/frontend/
# Usage: docker build -t todo-frontend:latest -f phase-4/docker/frontend.Dockerfile phase-2/frontend/

# --- Stage 1: Dependencies ---
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

# --- Stage 2: Builder ---
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_* vars are baked into the JS bundle at build time
ARG NEXT_PUBLIC_API_URL=http://todo-backend.todo-app.svc.cluster.local:7860/api
ARG NEXT_PUBLIC_AUTH_URL=http://localhost:3000
ARG NEXT_PUBLIC_CHAT_API_URL=http://todo-backend.todo-app.svc.cluster.local:7860
ARG NEXT_PUBLIC_VAPID_PUBLIC_KEY=""
ARG NEXT_PUBLIC_OPENAI_DOMAIN_KEY=""

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_AUTH_URL=$NEXT_PUBLIC_AUTH_URL \
    NEXT_PUBLIC_CHAT_API_URL=$NEXT_PUBLIC_CHAT_API_URL \
    NEXT_PUBLIC_VAPID_PUBLIC_KEY=$NEXT_PUBLIC_VAPID_PUBLIC_KEY \
    NEXT_PUBLIC_OPENAI_DOMAIN_KEY=$NEXT_PUBLIC_OPENAI_DOMAIN_KEY \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# --- Stage 3: Runner ---
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Create non-root user (node:20-alpine already has UID 1000 as 'node')
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy standalone output
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000 \
    HOSTNAME="0.0.0.0"

# Runtime server-side env vars (injected by Kubernetes Secrets/ConfigMap)
# CHAT_BACKEND_URL - phase-3 backend URL for /api/chat proxy
# DATABASE_URL - Neon PostgreSQL for Better Auth
# BETTER_AUTH_SECRET - JWT signing secret
# BETTER_AUTH_URL - Better Auth base URL

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/api/health || exit 1

CMD ["node", "server.js"]
