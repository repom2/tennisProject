#!/usr/bin/env bash

set -e

WAIT_FOR_TIMEOUT="${WAIT_FOR_TIMEOUT:-30}"
POETRY_INSTALL=${POETRY_INSTALL:-false}

if [ ${POETRY_INSTALL} == "true" ]; then
	echo -e "\e[34m >>> Poetry install \e[97m"
	poetry install
	echo -e "\e[32m >>> Poetry install completed \e[97m"
fi

for f in /docker-entrypoint.d/*; do
	case "$f" in
	*.sh)
		echo "$0: running $f"
		. "$f"
		;;
	*) echo "$0: ignoring $f" ;;
	esac
	echo
done

if [ "$1" = 'server' ]; then
	exec '/app/tennisproject'
else
  echo "hello"
	exec "$@"
fi
