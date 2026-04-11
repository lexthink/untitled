# define an alias for the specific node version used in this file.
FROM node:25-slim

# enable pnpm via corepack
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# Dependencies are installed here to ensure they will be cached.
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# copy application code
COPY . ${APP_HOME}

CMD ["pnpm", "dev", "--host", "0.0.0.0"]
