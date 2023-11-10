#!/bin/sh

template="/usr/share/nginx/html/config.js.template"
output="/usr/share/nginx/html/config.js"

if [ -n "$NODE_VERSION" ]; then
	echo "Running in nodejs container, assuming dev environment"

	template="/app/public/config.js.template"
	output="/app/public/config.js"

	echo "Environment:"
	env
fi

set -e

if [ -z "$IAM_APP_BASE_URL" ]; then
	echo "Error: IAM_APP_BASE_URL is not set"
	exit 1
fi

if [ -z "$GTM_ID" ]; then
	echo "Warning: GTM_ID is not set"
fi

if [ -z "$ENVIRONMENT" ]; then
	echo "Warning: ENVIRONMENT is not set, assuming production"
	export ENVIROMENT=production
fi

echo "Generating ${output} from ${template}"
envsubst '$IAM_APP_BASE_URL,$GTM_ID,$ENVIRONMENT' <"$template" >"$output"

exit 0
