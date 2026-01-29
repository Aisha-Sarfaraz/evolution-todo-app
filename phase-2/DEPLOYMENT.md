# Deployment Guide

This guide covers deploying the Phase 2 Todo Application to production.

## Architecture

- **Backend**: FastAPI (Python 3.13) deployed to Hugging Face Spaces
- **Frontend**: Next.js 16 deployed to Vercel
- **Database**: PostgreSQL (Neon, Supabase, or Railway)

## Prerequisites

1. GitHub repository with the code
2. Accounts on:
   - [Hugging Face](https://huggingface.co) (backend)
   - [Vercel](https://vercel.com) (frontend)
   - [Neon](https://neon.tech) or similar (PostgreSQL database)

## Environment Variables

### Backend (Hugging Face Spaces)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |
| `BETTER_AUTH_SECRET` | Secret key for auth (32+ chars) | `openssl rand -base64 32` |
| `BETTER_AUTH_URL` | Better Auth JWKS URL | `https://todo.vercel.app` |
| `BETTER_AUTH_ISSUER` | JWT issuer URL | `https://todo.vercel.app` |
| `BETTER_AUTH_AUDIENCE` | JWT audience URL | `https://todo.vercel.app` |
| `CORS_ORIGINS` | CORS allowed origins (comma-separated) | `https://todo.vercel.app` |
| `ENVIRONMENT` | Environment name | `production` |

### Frontend (Vercel)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://your-space.hf.space/api` |
| `NEXT_PUBLIC_AUTH_URL` | Auth URL for Better Auth | `https://todo.vercel.app` |
| `BETTER_AUTH_SECRET` | Better Auth secret (32+ chars) | Same as backend |
| `DATABASE_URL` | PostgreSQL for Better Auth | Same as backend |

## Deployment Steps

### 1. Deploy Database

**Using Neon (Recommended):**

1. Create a new Neon project at [neon.tech](https://neon.tech)
2. Copy the connection string
3. Run migrations locally:
   ```bash
   cd phase-2/backend
   pip install -e .
   alembic upgrade head
   ```

### 2. Deploy Backend (Hugging Face Spaces)

**Option A: Create via Hugging Face UI**

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Choose "Docker" as the SDK
3. Set Space name (e.g., `todo-api`)
4. Set visibility (public or private)
5. Create the Space

**Option B: Upload files to the Space**

1. Clone your Space repository:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-api
   cd todo-api
   ```

2. Copy backend files:
   ```bash
   cp -r /path/to/phase-2/backend/* .
   ```

3. Push to Hugging Face:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push
   ```

**Configure Secrets in Hugging Face:**

1. Go to your Space Settings > Repository secrets
2. Add the following secrets:
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET`
   - `BETTER_AUTH_URL`
   - `BETTER_AUTH_ISSUER`
   - `BETTER_AUTH_AUDIENCE`
   - `CORS_ORIGINS`

**Important Notes:**
- Hugging Face Spaces uses port **7860** by default
- The Dockerfile is already configured for this
- Your API will be available at: `https://YOUR_USERNAME-todo-api.hf.space`

### 3. Deploy Frontend (Vercel)

1. Connect GitHub repo to Vercel
2. Set root directory to `phase-2/frontend`
3. Configure environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` = `https://YOUR_USERNAME-todo-api.hf.space/api`
   - `NEXT_PUBLIC_AUTH_URL` = `https://your-vercel-domain.vercel.app`
   - `BETTER_AUTH_SECRET` = (same as backend)
   - `DATABASE_URL` = (same as backend)
4. Deploy

**Manual deployment:**
```bash
cd phase-2/frontend
npm install
vercel --prod
```

### 4. Update CORS After Deployment

After getting your Vercel URL, update the `CORS_ORIGINS` secret in Hugging Face Spaces:
```
CORS_ORIGINS=https://your-app.vercel.app
```

### 5. Verify Deployment

Run smoke tests:

```bash
# Check backend health
curl https://YOUR_USERNAME-todo-api.hf.space/health

# Check API root
curl https://YOUR_USERNAME-todo-api.hf.space/

# Check frontend
curl https://your-app.vercel.app

# Test signup endpoint
curl https://YOUR_USERNAME-todo-api.hf.space/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","name":"Test User"}'
```

## Security Checklist

- [ ] BETTER_AUTH_SECRET is at least 32 characters
- [ ] Database uses SSL (`sslmode=require`)
- [ ] CORS restricted to production frontend domain only
- [ ] Environment is set to `production`
- [ ] Rate limiting is enabled (100 req/min default)
- [ ] Hugging Face Space secrets are properly configured

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` format includes `?sslmode=require`
- Check SSL mode is enabled for Neon/Supabase
- Ensure IP allowlisting is configured (if applicable)

### CORS Errors
- Update `CORS_ORIGINS` in Hugging Face secrets to include your Vercel domain
- Check for trailing slashes in URLs (remove them)
- Ensure both HTTP and HTTPS are not mixed

### Authentication Issues
- Verify `BETTER_AUTH_SECRET` matches between frontend and backend
- Check `BETTER_AUTH_URL` points to correct frontend URL
- Ensure `NEXT_PUBLIC_API_URL` points to your Hugging Face Space

### Hugging Face Spaces Issues
- Check Space logs in the "Logs" tab
- Verify all secrets are set correctly
- Space may take a few minutes to build on first deploy
- Free tier Spaces may sleep after inactivity (upgrade to avoid)

## API Documentation

Once deployed, access API documentation at:
- Swagger UI: `https://YOUR_USERNAME-todo-api.hf.space/docs`
- ReDoc: `https://YOUR_USERNAME-todo-api.hf.space/redoc`
- OpenAPI JSON: `https://YOUR_USERNAME-todo-api.hf.space/openapi.json`
