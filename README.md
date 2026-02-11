# Project Chandra Deployment Guide

## 1) Backend containerization and runtime configuration

The backend remains containerized with the repository `Dockerfile` and is now configurable via environment variables:

- `FLASK_ENV` (default: `production`)
- `APP_HOST` (default: `0.0.0.0`)
- `APP_PORT` (default: `5000`)
- `MAX_CONTENT_LENGTH_MB` (default: `16`)
- `OUTPUT_DIR` (default: `/app/uploads`)
- `GUNICORN_WORKERS` (default: `2`)
- `GUNICORN_TIMEOUT` (default: `120`)
- `CORS_ALLOWED_ORIGINS` (default: `*`)

The container no longer launches Flask's development server directly. It uses Gunicorn in the `CMD`.

## 2) Reverse proxy and static hosting plans

### Option A (single stack): Nginx serves frontend + proxies API to Flask/Gunicorn

Use `docker-compose.option-a.yml`.

- Nginx serves static files from `frontend/`
- API traffic to `/api/*` is proxied to backend Flask/Gunicorn
- Uploaded images persist in a named Docker volume

Run:

```bash
docker compose -f docker-compose.option-a.yml up --build
```

Then:

- Frontend: `http://localhost:8080`
- Backend API through Nginx: `http://localhost:8080/api/...`

### Option B (split hosting): frontend on Vercel/Netlify/S3 + Flask API separately

Host frontend as static assets and deploy backend container independently (for example in ECS, Cloud Run, Azure Container Apps, Render, Fly.io, etc.).

Set Flask CORS allow-list:

```bash
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

Also ensure the frontend API base URL points to the backend domain.

## 3) Production process in container

Runtime process is now Gunicorn:

```bash
gunicorn --bind ${APP_HOST}:${APP_PORT} --workers ${GUNICORN_WORKERS} --timeout ${GUNICORN_TIMEOUT} app:app
```

This is WSGI production-ready and compatible with standard reverse-proxy deployment patterns.

## 4) CI/CD workflow

GitHub Actions workflow is defined in `.github/workflows/ci-cd.yml` and performs:

1. Lint (`ruff check .`)
2. Type check (`mypy app.py`)
3. Unit tests (`python -m unittest discover -s tests -p 'test_*.py' -v`)
4. Docker build
5. Container vulnerability scan (Trivy + SARIF upload)
6. Image push to GHCR on `main` or tagged release (`v*`)

## 5) Deployment targets and release strategy

### Environments

- **Staging**: automatic deploy from `main`
- **Production**: deploy from signed/approved semantic tags (for example `v1.2.0`)

### Suggested flow

1. Merge to `main` -> CI passes -> image published with `sha-<commit>` and `main`
2. Deploy `sha-<commit>` image to staging and run smoke tests (`/health`, upload endpoint)
3. Promote by creating release tag `vX.Y.Z`
4. Production deployment consumes immutable `vX.Y.Z` image tag

### Rollback strategy

- Keep the last known-good production tag (for example `v1.1.3`)
- If errors occur, redeploy previous tag immediately
- Use health checks and readiness checks to gate rollout
- Prefer rolling/canary updates when supported

### Tagged release policy

- `vMAJOR.MINOR.PATCH` for production images
- Optional pre-release tags (`v1.3.0-rc.1`) for staging candidate validation
