###########################################################
# Develoment image
ARG VARIANT="16-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/typescript-node:0-${VARIANT} as development

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends gettext-base

WORKDIR /
COPY docker/dev/docker-entrypoint.sh /
#COPY docker/docker-entrypoint.d /docker-entrypoint.d

# Add a work directory
WORKDIR /app

# Cache and Install dependencies
COPY package.json .
COPY yarn.lock .
RUN yarn install --prefer-offline --frozen-lockfile


# Copy app files
COPY . .

# Expose port
EXPOSE 3000

# Start the app
ENTRYPOINT [ "/docker-entrypoint.sh" ]
CMD [ "yarn", "start" ]

###########################################################
# Stage for running tests in a docker container
FROM node:16-alpine AS ci
LABEL test=true

WORKDIR /app

COPY package.json .
COPY yarn.lock .
RUN yarn install --frozen-lockfile

COPY . .
# never returns a failure, so success should be checked from reports in the CI pipeline
RUN CI=true yarn test --coverage --reporters=default --reporters=jest-junit; true
# results are in /app/junit.xml and /app/coverage

###########################################################
# Production image builder
FROM node:16-alpine AS builder
ARG DISABLE_ESLINT_PLUGIN=true

# Add a work directory
WORKDIR /app

# Cache and Install dependencies
COPY package.json .
COPY yarn.lock .
RUN yarn install --frozen-lockfile

# Copy app files
COPY . .

# Build the app
RUN yarn build

###########################################################
# Production image
# Bundle static assets with nginx
FROM nginx:1.23-alpine AS production

#COPY docker/docker-entrypoint.d /docker-entrypoint.d
COPY docker/nginx/tennis-app.conf.template /etc/nginx/templates/default.conf.template

# Copy built assets from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

###########################################################
# Legacy Production image
# Bundle static assets with openresty (nginx)
FROM openresty/openresty:1.21.4.1-0-bullseye-fat AS legacy-production

# OIDC
# 1.7.5 needs lua-resty-session 4 and it does not seem to work at the moment
RUN opm get zmartzone/lua-resty-openidc=1.7.4 bungle/lua-resty-session=3.10 \
    && mkdir /docker-entrypoint.d

COPY docker/openresty/docker-entrypoint.sh /
#COPY docker/docker-entrypoint.d /docker-entrypoint.d
COPY docker/openresty/20-envsubst-on-templates.sh /docker-entrypoint.d

COPY docker/openresty/tennis-app.conf.template /etc/nginx/templates/default.conf.template

# Copy built assets from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

CMD ["/usr/bin/openresty", "-g", "daemon off;"]
ENTRYPOINT ["/docker-entrypoint.sh"]

