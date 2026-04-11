export COMPOSE_FILE := "docker-compose.local.yaml"

# Default command to list all available commands.
default:
    @just --list

# Build images.
build *args:
    @docker compose --profile full build {{args}}

# Start all containers.
up *args:
    @docker compose --profile full up --remove-orphans {{args}}

# Start only backend containers.
up-backend *args:
    @docker compose --profile backend up --remove-orphans {{args}}

# Start only frontend container.
up-frontend *args:
    @docker compose --profile frontend up --remove-orphans {{args}}

# Stop containers.
down:
    @docker compose --profile full down

# Remove containers and their volumes.
prune *args:
    @docker compose --profile full down -v {{args}}

# View container logs.
logs *args:
    @docker compose --profile full logs -f {{args}}

# Run a manage.py command.
manage +args:
    @docker compose run --rm backend python ./manage.py {{args}}

# Run migrations and seed the database.
seed:
    @docker compose run --rm backend python ./manage.py migrate
    @docker compose run --rm backend python ./manage.py seed

# Install all local dependencies.
install: install-backend install-frontend

# Install backend dependencies.
install-backend:
    cd backend && uv sync --locked

# Install frontend dependencies.
install-frontend:
    cd frontend && pnpm install

# Run tests.
test *args:
    @docker compose run --rm backend pytest {{args}}
