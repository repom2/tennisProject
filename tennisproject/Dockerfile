# Dockerfile
ARG VARIANT="3.11-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT} as development

# setup environment variable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=postgres://tennis:tennis@localhost:5432/tennis?connect_timeout=3
ENV DEBUG='true'
ENV POETRY_INSTALL='true'

ARG POETRY_VERSION="1.2.2"
RUN apt-get update && apt-get install -y --no-install-recommends\
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir poetry==${POETRY_VERSION}

#RUN apt-get install nginx vim -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
# RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log

# RUN chown -R www-data:www-data /app
USER root

COPY docker/tennisproject/docker-entrypoint.sh /
COPY docker/tennisproject/docker-entrypoint.d/ /docker-entrypoint.d

WORKDIR /app
# Create directory for dbt config
#RUN mkdir -p /app/tennisproject/dbt
# Copy dbt profile
#COPY profiles.yml /app/tennisproject/dbt/profiles.yml
COPY poetry.lock .
COPY pyproject.toml .
COPY README.md .

RUN poetry config virtualenvs.create false
RUN poetry install

COPY . .

# start server
EXPOSE 8000

ENTRYPOINT [ "/docker-entrypoint.sh" ]
CMD ["server", "nginx", "-g", "daemon off;"]

