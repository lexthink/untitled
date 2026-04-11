# Untitled

## Prerequisites

- [Docker](https://docs.docker.com/get-started/get-docker/)
- [just](https://github.com/casey/just) (optional)

## Local development

### Build

```bash
just build
```

### Start

```bash
just up              # everything (backend + frontend)
just up-backend      # only backend
just up-frontend     # only frontend
just up --detach     # run in background
```

### Services

| Service  | URL                    | Profile  |
|----------|------------------------|----------|
| Frontend | http://localhost:4321  | frontend |
| Backend  | http://localhost:8000  | backend  |
| Flower   | http://localhost:5555  | backend  |
| Mailpit  | http://localhost:8025  | backend  |

## Documentation

- [Development](docs/development.md) — setup, workflow, adding dependencies
- [Architecture](docs/architecture.md) — multi-tenancy, schemas, auth
- [Organization Management](docs/organization-management.md) — invitations, roles, ownership, audit
- [Permissions](docs/permissions.md) — roles, API and admin permissions
- [Celery Tasks](docs/celery-tasks.md) — organization-aware tasks
- [Migrations](docs/migrations.md) — shared vs organization migrations, deploy workflow
- [Seed](docs/seed.md) — seed command, fixtures, adding new data
- [Testing](docs/testing.md) — fixtures, factories, organization context in tests
- [Considerations](docs/considerations.md) — backups, rate limiting, cache, file uploads, signals
- [Deployment](docs/deployment.md) — production build, scaling, supervisor

### Useful commands

```bash
just seed                    # run migrations and load fixtures
just test                    # run tests
just logs                    # all logs
just logs backend            # single service
just manage createsuperuser  # run manage.py commands
just down                    # stop containers
just prune                   # stop and remove volumes
```

### Without just

```bash
export COMPOSE_FILE=docker-compose.local.yaml

docker compose --profile full up -d
docker compose --profile full logs -f
docker compose --profile full down
docker compose run --rm backend python manage.py createsuperuser
```

## Production

See [Deployment](docs/deployment.md).
