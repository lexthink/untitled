# Development

## Prerequisites

- [Docker](https://docs.docker.com/get-started/get-docker/)
- [just](https://github.com/casey/just)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [pnpm](https://pnpm.io/) (Node package manager)

## Stack versions

| Tool | Version | Defined in |
|---|---|---|
| Python | 3.14 | `backend/.python-version` |
| Node | >= 22.12.0 | `frontend/package.json` |
| pnpm | 8.11.0 | `frontend/package.json` |
| PostgreSQL | 18 | `docker-compose.local.yaml` |
| Redis | 7.2 | `docker-compose.local.yaml` |

## Initial setup

### 1. Clone the repo

```bash
git clone git@github.com:lexthink/untitled.git
cd untitled
```

### 2. Install local dependencies

```bash
just install
```

This creates `backend/.venv` and `frontend/node_modules`.

### 3. Install pre-commit hooks

```bash
pre-commit install
```

### 4. Build and start containers

```bash
just build
just up --detach
```

### 5. Seed the database

```bash
just seed
```

## Day-to-day workflow

### Start containers

```bash
just up                  # foreground (see logs)
just up --detach         # background
just up-backend          # only backend
just up-frontend         # only frontend
```

### Run tests

```bash
just test
```

### Run a manage.py command

```bash
just manage migrate
just manage createsuperuser
just manage shell
```

### View logs

```bash
just logs                # all
just logs backend        # single service
```

### Stop containers

```bash
just down                # stop
just prune               # stop and remove volumes
```

## Adding dependencies

### Backend (Python)

```bash
cd backend
uv add <package>         # production dependency
uv add --dev <package>   # dev dependency
```

Then rebuild the Docker image:

```bash
just build backend
```

### Frontend (Node)

```bash
cd frontend
pnpm add <package>
pnpm add -D <package>    # dev dependency
```

Then rebuild the Docker image:

```bash
just build frontend
```

## Editor setup

Open the project from the root:

```bash
code .
```

VS Code settings and recommended extensions are in `.vscode/`. The Python interpreter is configured to use `backend/.venv`.

## Services

| Service  | URL                    | Profile  |
|----------|------------------------|----------|
| Backend  | http://localhost:8000  | backend  |
| Flower   | http://localhost:5555  | backend  |
| Mailpit  | http://localhost:8025  | backend  |
| Frontend | http://localhost:4321  | frontend |
