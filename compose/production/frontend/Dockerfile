# define an alias for the specific node version used in this file.
# Node build stage
FROM node:25-slim AS node-build-stage

# install pnpm
RUN npm install -g pnpm

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# Dependencies are installed here to ensure they will be cached.
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# copy application code and build
COPY . ${APP_HOME}
RUN pnpm build

# Run stage — serve static files
FROM node:25-slim AS node-run-stage

RUN npm install -g serve

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

# copy the built static files
COPY --from=node-build-stage ${APP_HOME}/dist ${APP_HOME}/dist

CMD ["serve", "dist", "-l", "4321"]
