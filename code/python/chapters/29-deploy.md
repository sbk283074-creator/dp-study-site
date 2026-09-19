---
chapter: 29
part: 4
title: "Deploy: Docker, CI & the Cloud"
summary: Package StudyHub into a hardened container, run Postgres and migrations alongside it, put a reverse proxy in front, and ship it through CI with logging, health checks, backups and a rollback plan.
minutes: 50
tags: [docker, docker-compose, alembic, ci, gunicorn, caddy, deployment]
---

Running on your laptop proves the code works. Shipping means other people depend on it, and five
things change at once: the reload flag goes away, several processes run in parallel, the database
is real and shared, secrets live outside your source tree, and every failure now needs a log you
can read after the fact. None of that is exotic — it is a short list of decisions you make once
per project. This chapter makes them for StudyHub, in the order you will actually hit them.

## What production changes

| Development | Production |
| --- | --- |
| `uvicorn --reload` | `uvicorn --workers N` or gunicorn + uvicorn workers |
| SQLite file | Postgres (or another real server) with a volume and backups |
| `create_all()` at startup | Alembic migrations run as a distinct deploy step |
| `.env` on disk | Environment variables from your host's secret store |
| Print statements | JSON logs to stdout with request IDs |
| "It works on my machine" | Health checks, monitoring, and a rollback you have rehearsed |

## Configuration through the environment

`pydantic-settings` (Chapter 27) already reads the environment. Production just supplies
different values. The rule: **the image contains code, never configuration.** If a secret is in
the image, anyone who can pull the image can read it, and the same image cannot be promoted from
staging to production.

```python
# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "StudyHub"
    debug: bool = False
    database_url: str = "sqlite:///./studyhub.db"
    secret_key: str          # required — no default, fails fast at boot
    cors_origins: list[str] = []
    sentry_dsn: str | None = None
    log_level: str = "INFO"
```

Removing the default from `secret_key` is deliberate. A missing variable now crashes at startup
with a clear message instead of silently signing tokens with a key that is in the public FastAPI
repository.

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
eval "$(python3 -c "import secrets; print(f'export SECRET_KEY={secrets.token_urlsafe(48)}')")"
```

## Migrations with Alembic

`create_all()` cannot add a column to a table that has data in it. Migrations can.

```bash
alembic init migrations
```

Edit `migrations/env.py` to import your models and read the URL from settings:

```python
# migrations/env.py (key lines)
from app.models import Base
from app.settings import get_settings

config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata
```

```bash
alembic revision --autogenerate -m "add decks and cards"
alembic upgrade head
alembic downgrade -1
```

Autogenerate is a draft, not an answer. Read every generated migration before committing it —
it misses table renames it cannot infer, and it will happily generate a `DROP COLUMN` you did not
mean.

## Process management: how many workers

One Python process handles one request at a time unless it is async. StudyHub is async, so a
single worker handles many concurrent connections, but it still uses one CPU core. Add workers to
use the rest:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

- **Async app:** start with 1 worker per core. A 2-core container → 2 or 3 workers.
- **Blocking work** (sync `def` endpoints, heavy CPU): gunicorn with `UvicornWorker` and roughly
  `2 × cores + 1` workers, because sync endpoints occupy a worker for their whole duration.
- **Hard ceiling:** memory. Each worker is a separate process with its own copy of the app. Four
  workers at 300 MB each in a 1 GB container is an OOM kill waiting for a traffic spike.

```bash
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --graceful-timeout 30 \
  --access-logfile -
```

Gunicorn also gives you a supervisor: it restarts workers that die, and `--graceful-timeout`
lets in-flight requests finish during a rolling deploy. If your platform can run several
containers, prefer more small containers over many workers in one — a crashed container is
replaced, a crashed worker is only restarted.

## The Dockerfile

```dockerfile
# syntax=docker/dockerfile:1

# ---------- build stage ----------
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN groupadd --gid 10001 app \
 && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app alembic.ini ./
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app app ./app
COPY --chown=app:app docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz').status==200 else 1)"

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

Why each piece:

- **Multi-stage.** The builder keeps pip's cache, compilers and headers; the runtime gets only
  `/opt/venv`. Expect roughly 1 GB down to under 200 MB — faster pushes, smaller attack surface.
- **`--no-cache-dir`.** A Docker layer keeps whatever you write in it, so a pip cache is dead
  weight you ship forever.
- **Non-root `USER app`.** A container escape or RCE should not land as root. `10001` is a
  conventional unprivileged UID.
- **`PYTHONUNBUFFERED=1`.** Without it, Python buffers stdout and your logs appear minutes late,
  or never, if the process is killed.
- **`HEALTHCHECK`** — the platform restarts a container whose process is alive but wedged.

```text
# .dockerignore
.venv/
__pycache__/
*.py[cod]
.git/
.gitignore
.env
.env.*
tests/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.db
*.sqlite3
.DS_Store
```

`.env` in `.dockerignore` is the last line of defence against baking secrets into an image. The
build context is also your build time: excluding `.git` and `.venv` can turn a 90-second build
into five.

## Entrypoint and migrations on deploy

```bash
#!/usr/bin/env bash
# docker-entrypoint.sh
set -euo pipefail

# Take an advisory lock so only one container migrates at a time.
python - <<'PY'
import os, sqlalchemy
url = os.environ["DATABASE_URL"]
engine = sqlalchemy.create_engine(url, pool_pre_ping=True)
with engine.connect() as conn:
    conn.execute(sqlalchemy.text("SELECT pg_advisory_lock(424242)"))
    conn.commit()
    print("acquired migration lock")
PY

alembic upgrade head
exec "$@"
```

`exec "$@"` replaces the shell with your `CMD`, so uvicorn becomes PID 1 and receives
`SIGTERM` directly — that is what allows a graceful shutdown instead of a 10-second timeout and a
`SIGKILL`.

The better option, when your platform supports it, is a **release step**: run migrations once
before new containers start (Fly.io `release_command`, a Railway deploy command, a Kubernetes
`Job`, or `docker compose run --rm api alembic upgrade head` before `up`). The advisory lock above
is the fallback for platforms that only give you an entrypoint.

## docker compose with Postgres

```yaml
# compose.yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: studyhub
      POSTGRES_PASSWORD: studyhub
      POSTGRES_DB: studyhub
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U studyhub -d studyhub"]
      interval: 5s
      timeout: 3s
      retries: 10

  api:
    build: .
    env_file: .env
    environment:
      DATABASE_URL: postgresql+psycopg://studyhub:studyhub@db:5432/studyhub
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    restart: unless-stopped

volumes:
  pgdata:
```

```bash
docker compose run --rm api alembic upgrade head
docker compose up -d --build
docker compose logs -f api
```

The named volume `pgdata` is what makes your database survive `docker compose down`. Without it,
`down` deletes the container and every row with it. Use `depends_on: condition: service_healthy`
rather than a plain `depends_on` — Postgres accepts connections briefly while it is still
initialising, and "starts" is not the same as "ready".

## Reverse proxy

Your app should never serve TLS or static files itself. Put a proxy in front that terminates TLS,
compresses, and serves `/static` from disk.

Caddy, which obtains and renews Let's Encrypt certificates automatically:

```text
studyhub.example.com {
	encode gzip
	reverse_proxy api:8000

	handle_path /static/* {
		root * /srv/static
		file_server
	}
	log {
		output stdout
		format json
	}
}
```

nginx, if you would rather configure it explicitly:

```text
server {
    listen 443 ssl http2;
    server_name studyhub.example.com;

    ssl_certificate     /etc/letsencrypt/live/studyhub.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/studyhub.example.com/privkey.pem;

    location /static/ {
        alias /srv/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

Forwarding `X-Forwarded-Proto` matters: FastAPI uses it to build correct redirect URLs and to
decide whether your `Secure` cookies are acceptable.

## Structured logging and request IDs

Plain text logs are unsearchable at any volume. Emit one JSON object per line and add a request
ID so you can follow a single request across workers.

```python
# app/logging_config.py
import contextvars
import json
import logging

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id.get(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
```

```python
import uuid

from fastapi import Request


@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    token = request_id.set(rid)
    try:
        response = await call_next(request)
    finally:
        request_id.reset(token)
    response.headers["X-Request-ID"] = rid
    return response
```

`contextvars` is the correct mechanism here: each async task gets its own copy, so two concurrent
requests cannot overwrite each other's ID. Return the ID in a response header so a user reporting
a bug can paste it into a support ticket and you can find the exact request.

## Health checks: liveness vs readiness

Two different questions deserve two endpoints.

```python
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(tags=["ops"])


@router.get("/healthz")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
def readiness(session: SessionDep) -> JSONResponse:
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse({"status": "unavailable"}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return JSONResponse({"status": "ready"})
```

`/healthz` only proves the process is alive — it must never touch the database, or a brief
database blip will cause your platform to restart every healthy container. `/readyz` checks
dependencies and is what a load balancer should poll before routing traffic.

## Continuous integration

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: pip

      - name: Install
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint
        run: ruff check . && ruff format --check .

      - name: Types
        run: mypy app

      - name: Tests
        run: pytest -q --cov=app --cov-report=term-missing

  image:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Build image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: studyhub:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Build the image even when you do not push it — that is the only way CI catches a Dockerfile that
no longer matches your `requirements.txt`. Cache layers (`type=gha`) turn a five-minute build into
forty seconds.

## Hosting options

| Option | Cost from | Complexity | Good for |
| --- | --- | --- | --- |
| **Fly.io** | ~$5/month | Medium | Global deploys, VMs close to users, Postgres with automatic backups |
| **Railway** | ~$5/month | Low | Fastest path from repo to URL; usage-based billing |
| **Render** | Free tier then ~$7/month | Low | Simple web service + managed Postgres, generous free tier |
| **VPS** (Hetzner, DigitalOcean) | ~$5/month | High | Full control, best price per GB, you own patching, backups, TLS |
| **PaaS containers** (Cloud Run, Azure Container Apps) | Pay per request | Medium | Spiky traffic, scale to zero |

Pick the cheapest option that removes a task you do not want to own. If you have never
administered a Linux server, a PaaS is not a shortcut — it buys back the weeks you would spend on
systemd, certbot and firewall rules. Move to a VPS when the bill justifies it.

## Backups, rollback and monitoring

Backups you have not restored are not backups.

```bash
#!/usr/bin/env bash
# backup.sh — run from cron on a separate machine
set -euo pipefail
STAMP=$(date -u +%Y%m%dT%H%M%S)
docker compose exec -T db pg_dump -U studyhub studyhub | gzip > "/backups/studyhub-$STAMP.sql.gz"
find /backups -name '*.sql.gz' -mtime +30 -delete
```

```bash
gunzip -c /backups/studyhub-20260101T030000.sql.gz | psql -U studyhub -h localhost studyhub
```

Rehearse that restore command quarterly. A backup stored on the same disk as the database protects
you from exactly one failure mode.

For rollback, deploy **pinned image tags**, never `latest`:

```bash
docker pull registry.example.com/studyhub:$(git rev-parse --short HEAD)
docker compose up -d
# rollback
docker compose up -d --no-deps api   # with the previous tag in compose.yaml
```

This only works if migrations are backward compatible. Use expand → migrate → contract: add a
nullable column (expand), deploy code that writes both, backfill, switch reads, and only remove
the old column (contract) a release later. A migration that drops a column the previous version
still reads makes rollback impossible.

Minimum monitoring: an external uptime check hitting `/healthz` every minute, error tracking (a
`Sentry` SDK is three lines with `sentry_sdk.init(dsn=settings.sentry_dsn)`), and an alert when
`/readyz` fails twice in a row. Add database disk usage — running out of disk is the most common
cause of a total outage that no amount of code quality prevents.

## Pre-launch checklist

1. `debug=False`, `SECRET_KEY` from the environment, no `.env` in git or in the image.
2. `docker compose run --rm api alembic upgrade head` succeeds on a clean database.
3. `/healthz` and `/readyz` respond; the proxy forwards `X-Forwarded-Proto`.
4. TLS certificate issued and auto-renewing; HTTP redirects to HTTPS.
5. Backups scheduled **and** one restore rehearsed.
6. Logs are JSON, contain request IDs, and are shipped off the container.
7. Image tag pinned; rollback tested by deploying the previous tag.
8. `ruff`, `mypy` and `pytest` green in CI, and the image builds in CI.

:::pitfall Secrets in the image or in git, and migrations racing in every worker
Two failures with the same root cause — treating deployment as an afterthought. A `.env` copied
into the build context bakes every secret into a layer that anyone with image pull access can
read, and that git object is forever even after you delete the file. Meanwhile, an entrypoint that
runs `alembic upgrade head` in N containers at once means N processes try to create the same
tables: you get `relation "users" already exists`, or two half-applied migrations and a
distributed deadlock. Fix both structurally: `.dockerignore` and a secret store for the first,
a single release step (or an advisory lock) for the second.
:::

:::scenario The deploy "succeeded" and then everything broke
StudyHub's first real deploy: three containers start at once. The logs show two of them dying with
`sqlalchemy.exc.ProgrammingError: relation "users" already exists`, and the third comes up but
every user is logged out each time a container restarts. Rolling back by redeploying `latest`
changes nothing. Someone also notices the `.env` file is in the git history.
:::

:::solution Separate configuration from code, and make migrations a single-writer step
1. **Rotate the secret first.** Generate a new `SECRET_KEY`, put it in the platform's secret
   store, and restart. Everyone is signed out once; that is the correct price for a leaked key.
   Then `git rm --cached .env`, add `.env` to `.gitignore` and `.dockerignore`, and rewrite
   history (`git filter-repo`) if the repository is shared. A rotated secret plus a leaked old one
   is fine; an unrotated leaked secret is not.
2. **Pin tags so rollback means something.** `latest` is a moving pointer — redeploying it can
   redeploy the same broken build. Tag every image with the commit SHA and deploy the SHA. Rollback
   becomes "deploy the previous SHA", which is testable.
3. **Migrate once.** Add a release command that runs `alembic upgrade head` before new containers
   accept traffic: `docker compose run --rm api alembic upgrade head`, or `release_command` on
   Fly.io, or a Kubernetes `Job`. Where only an entrypoint is available, take
   `pg_advisory_lock(<fixed id>)` around the migration so exactly one runner proceeds.
4. **Stop the restart loop from being invisible.** Point the container `HEALTHCHECK` at `/healthz`
   and the load balancer at `/readyz`, and alert on repeated restarts. The outage lasted as long
   as it did because nothing was watching.

The underlying lesson: deployment is part of the program. The same care you put into a transaction
boundary belongs on "who runs this migration, and when".
:::

## Key takeaways

- Production differs from development in six concrete ways: no reload, multiple workers, a real
  database, external secrets, structured logs and health checks.
- Configuration comes from the environment; the image holds code only, and `.dockerignore` keeps
  `.env` out of the build context.
- A multi-stage Dockerfile with a non-root user, `--no-cache-dir`, and a `HEALTHCHECK` produces a
  small, safe image; `exec "$@"` in the entrypoint makes your server PID 1 so it can shut down
  gracefully.
- Run `alembic upgrade head` once per deploy as a release step, or guard it with a Postgres
  advisory lock — never in every worker simultaneously.
- Use roughly one async worker per core, or `2 × cores + 1` for blocking work, bounded by memory.
- A reverse proxy terminates TLS, serves static files and forwards `X-Forwarded-Proto`; liveness
  (`/healthz`) and readiness (`/readyz`) are separate endpoints.
- Deploy pinned image tags, keep migrations backward compatible, schedule backups and rehearse a
  restore.

## Practice

- [ ] Write a multi-stage `Dockerfile` and `.dockerignore` for StudyHub, build it, and run
      `docker run --rm -p 8000:8000 -e SECRET_KEY=... studyhub:dev` to confirm `/healthz`
      responds.
- [ ] Add `compose.yaml` with Postgres and a named volume; verify data survives
      `docker compose down && docker compose up -d`.
- [ ] Generate an Alembic migration for a new `cards.review_count` column, apply it, and confirm
      `alembic downgrade -1` reverses it cleanly.
- [ ] Add `/readyz` that returns 503 when the database is unreachable, and wire the container
      `HEALTHCHECK` to `/healthz`.
- [ ] Add a GitHub Actions workflow running `ruff check`, `mypy app`, `pytest` and a Docker build,
      and make it fail on a deliberate lint error.
- [ ] Write a one-page `RUNBOOK.md` covering: how to deploy, how to roll back, how to restore the
      database from backup, and who gets paged.

## Solutions

:::solution Exercise 1
```bash
docker build -t studyhub:dev .
docker run --rm -p 8000:8000 \
  -e SECRET_KEY="$(python3 -c 'import secrets;print(secrets.token_urlsafe(48))')" \
  -e DATABASE_URL="sqlite:///./studyhub.db" \
  studyhub:dev
```
```bash
curl -i http://127.0.0.1:8000/healthz
```
```text
HTTP/1.1 200 OK
content-type: application/json

{"status":"ok"}
```
Passing `SECRET_KEY` with `-e` rather than in the Dockerfile proves configuration is truly
external. If the container starts without it, your `Settings` class is missing the required field —
that failure at boot is exactly what you want in production.
:::

:::solution Exercise 2
```yaml
volumes:
  pgdata:
```
```bash
docker compose up -d
docker compose exec api python -c "
from app.models import Deck
from app.database import SessionLocal
with SessionLocal() as s: s.add(Deck(name='persisted', owner_id=1)); s.commit()"
docker compose down
docker compose up -d
docker compose exec db psql -U studyhub -c "select name from decks;"
```
```text
    name
------------
 persisted
```
The row survives because `pgdata` is a named volume with a lifecycle independent of the container.
Delete the volume (`docker compose down -v`) and the data goes with it — which is precisely why the
backup script in the chapter is not optional.
:::

:::solution Exercise 3
```bash
alembic revision --autogenerate -m "add review_count to cards"
alembic upgrade head
alembic downgrade -1
```
```python
def upgrade() -> None:
    op.add_column("cards", sa.Column("review_count", sa.Integer(), nullable=False,
                                     server_default="0"))
    op.alter_column("cards", "review_count", server_default=None)


def downgrade() -> None:
    op.drop_column("cards", "review_count")
```
`server_default="0"` is what lets a `NOT NULL` column be added to a table that already has rows;
dropping the default afterwards keeps new inserts explicit. Always implement `downgrade()` — a
migration you cannot reverse is a rollback you cannot perform.
:::

:::solution Exercise 4
```python
@router.get("/readyz")
def readiness(session: SessionDep) -> JSONResponse:
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse({"status": "unavailable"},
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return JSONResponse({"status": "ready"})
```
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz').status==200 else 1)"
```
`start-period` gives migrations and import time a grace window before failures count. Test the
503 path by pointing `DATABASE_URL` at a closed port in a scratch container — an untested failure
path is a guess, not a safety net.
:::

:::solution Exercise 5
```yaml
      - name: Lint
        run: |
          ruff check .
          ruff format --check .
      - name: Types
        run: mypy app
      - name: Tests
        run: pytest -q
      - name: Build image
        run: docker build -t studyhub:${{ github.sha }} .
```
```bash
# verify locally that CI would actually fail
printf 'import os\nx=1\n' > app/lintme.py
ruff check .
```
```text
app/lintme.py:1:1: F401 'os' imported but unused
app/lintme.py:1:8: E225 missing whitespace around operator
Found 2 errors.
```
Run the same commands locally that CI runs; a pipeline you have never seen fail is a pipeline you
do not know works. The image build step catches the failure mode where `requirements.txt` and the
Dockerfile disagree.
:::

:::solution Exercise 6
```markdown
# RUNBOOK — StudyHub

## Deploy
1. `git switch main && git pull`
2. `SHA=$(git rev-parse --short HEAD)`
3. `docker build -t registry.example.com/studyhub:$SHA . && docker push ...`
4. `docker compose run --rm api alembic upgrade head`
5. Update the image tag in compose.yaml, then `docker compose up -d`
6. Check `/readyz` and the uptime monitor

## Roll back
1. Set the image tag to the previous SHA in compose.yaml
2. `docker compose up -d --no-deps api`
3. If the new release added a column, do NOT downgrade — deploy code that ignores it

## Restore the database
1. `docker compose stop api`
2. `gunzip -c /backups/studyhub-<stamp>.sql.gz | docker compose exec -T db psql -U studyhub studyhub`
3. `docker compose start api`

## Alerts
Uptime check on /healthz (1 min) -> on-call phone
/readyz failing twice -> on-call Slack
Disk > 80% -> on-call Slack
```
Writing the runbook surfaces the gaps: if you cannot write step 4 of the deploy, you do not have a
migration strategy yet. Keep it next to the code so the person fixing an outage at 3am is not the
person who has to remember how any of this works.
:::
