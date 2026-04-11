# define an alias for the specific node version used in this file.
# Node build stage
FROM node:25-slim AS node-build-stage

# enable pnpm via corepack
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# Dependencies are installed here to ensure they will be cached.
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# copy application code and build
COPY . ${APP_HOME}
RUN pnpm build

# Node 'run' stage
FROM node:25-slim AS node-run-stage

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# copy the built application from the builder
COPY --from=node-build-stage ${APP_HOME}/dist ${APP_HOME}/dist
COPY --from=node-build-stage ${APP_HOME}/node_modules ${APP_HOME}/node_modules
COPY --from=node-build-stage ${APP_HOME}/package.json ${APP_HOME}/package.json

CMD ["node", "./dist/server/entry.mjs"]
