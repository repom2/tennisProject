#!/bin/sh
set -e

if [ "${1}" = "yarn" ] && [ "${2}" = "start" ]; then
	if /usr/bin/find "/docker-entrypoint.d/" -mindepth 1 -maxdepth 1 -type f -print -quit 2>/dev/null | read v; then
		echo "$0: /docker-entrypoint.d/ is not empty, will attempt to perform configuration"

		echo "$0: Looking for shell scripts in /docker-entrypoint.d/"
		find "/docker-entrypoint.d/" -follow -type f -print | sort -V | while read -r f; do
			case "$f" in
			*.sh)
				if [ -x "$f" ]; then
					echo "$0: Launching $f"
					"$f"
				else
					# warn on shell scripts without exec bit
					echo "$0: Ignoring $f, not executable"
				fi
				;;
			*) echo "$0: Ignoring $f" ;;
			esac
		done

		echo "$0: Configuration complete; ready for start up"
	else
		echo "$0: No files found in /docker-entrypoint.d/, skipping configuration"
	fi

	export YARN_INSTALL="${YARN_INSTALL:-true}"

	echo ">>> Environment variables:"
	echo "YARN_INSTALL=${YARN_INSTALL}"

	if [ "${YARN_INSTALL}" = "true" ]; then
		echo ">>> yarn install"
		yarn install
	fi
fi

exec "$@"
