#!/usr/bin/env bash

set -e

WAIT_FOR_TIMEOUT="${WAIT_FOR_TIMEOUT:-30}"

if [ -n "$DATABASE_URL" ]
then
    DB_HOST=`echo ${DATABASE_URL} | sed -E 's/[^@]+@?(.+):[0-9]+.*$/\1/'` # //<host>:
: "${DB_HOST:?DB_HOST not parsed}"

    DB_PORT=`echo ${DATABASE_URL} | sed -E 's/[^@]+@?(.+):([0-9]+).*$/\2/'` # :<port>/
: "${DB_PORT:?5432}"

    echo "Waiting for Postgres ${DB_HOST}:${DB_PORT}"
    timeout ${WAIT_FOR_TIMEOUT} bash -c 'until printf "" 2>>/dev/null >>/dev/tcp/$0/$1; do sleep 1; done' ${DB_HOST} ${DB_PORT}
    echo "Postgres ${DB_HOST}:${DB_PORT} ok"
fi
