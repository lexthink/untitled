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

| Service  | URL                          | Profile  |
|----------|------------------------------|----------|
| API      | http://localhost:8000        | backend  |
| Admin    | http://localhost:8000/admin/ | backend  |
| Flower   | http://localhost:5555        | backend  |
| Mailpit  | http://localhost:8025        | backend  |
| Frontend | http://localhost:4321        | frontend |

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

```bash
docker compose -f docker-compose.production.yaml --profile full up -d
```
