# Deployment

## Environment variables

Before deploying, create the production env files:

```
.envs/.production/.backend
.envs/.production/.postgres
.envs/.production/.frontend
```

These files are **not** committed to the repository. See `.envs/.local/` for reference.

Set the `DOMAIN` environment variable — either export it or pass it inline with compose commands. Subdomains are built automatically (`backend.DOMAIN`, `app.DOMAIN`, etc.):

```bash
# Option 1: export once
export DOMAIN=untitled.com

# Option 2: pass inline per command
DOMAIN=untitled.com docker compose -f docker-compose.production.yaml up -d
```

## DNS

Configure the following DNS records pointing to your server (where `DOMAIN` is your domain):

| Subdomain | Service |
|---|---|
| `traefik.DOMAIN` | Traefik dashboard |
| `app.DOMAIN` | Frontend |
| `backend.DOMAIN` | Backend API |
| `flower.DOMAIN` | Flower (Celery monitoring) |

## Building & Running Production Stack

Build the stack:

```bash
docker compose -f docker-compose.production.yaml build
```

Run it:

```bash
docker compose -f docker-compose.production.yaml up
```

Run detached (background):

```bash
docker compose -f docker-compose.production.yaml up -d
```

## Database

Run migrations:

```bash
docker compose -f docker-compose.production.yaml run --rm backend python manage.py migrate
```

Create a superuser:

```bash
docker compose -f docker-compose.production.yaml run --rm backend python manage.py createsuperuser
```

Open a Django shell:

```bash
docker compose -f docker-compose.production.yaml run --rm backend python manage.py shell
```

## Logs

View logs:

```bash
docker compose -f docker-compose.production.yaml logs
```

Follow logs for a specific service:

```bash
docker compose -f docker-compose.production.yaml logs -f backend
```

## Scaling

Scale backend or celery workers:

```bash
docker compose -f docker-compose.production.yaml up --scale backend=4
docker compose -f docker-compose.production.yaml up --scale celeryworker=2
```

Do **not** scale `postgres`, `celerybeat`, or `traefik`.

## Container status

```bash
docker compose -f docker-compose.production.yaml ps
```

## Process manager (supervisor)

To ensure the stack survives reboots, use a process manager like supervisor.

Create `/etc/supervisor/conf.d/untitled.conf`:

```ini
[program:untitled]
command=bash -c "export DOMAIN=untitled.com && docker compose -f docker-compose.production.yaml up"
directory=/path/to/untitled
redirect_stderr=true
autostart=true
autorestart=true
priority=10
```

Then run:

```bash
supervisorctl reread
supervisorctl update
supervisorctl start untitled
supervisorctl status
```
