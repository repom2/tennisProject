#!/usr/bin/env bash

set -e

if [ "$ENVIRONMENT" == "development" ] && [ "$DBT_DEPS" == "true" ]; then
	echo "dbt deps:"
	poetry run dbt deps --project-dir dbt/zendesk_metrics
fi
