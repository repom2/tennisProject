#!/bin/sh
# shellcheck disable=SC3043

# From:
# https://raw.githubusercontent.com/nginxinc/docker-nginx/master/stable/debian/20-envsubst-on-templates.sh

set -e

export OIDC_DEFAULT_ROLE="${OIDC_DEFAULT_ROLE:-}"
export DNS_RESOLVER="${DNS_RESOLVER:-1.1.1.1}"

if [ -z "${OIDC_DISCOVERY_URL}" ]; then
    export OIDC_DISCOVERY_URL="${OIDC_ISSUER}/.well-known/openid-configuration"
fi

ME=$(basename "$0")

auto_envsubst() {
  local template_dir="${NGINX_ENVSUBST_TEMPLATE_DIR:-/etc/nginx/templates}"
  local suffix="${NGINX_ENVSUBST_TEMPLATE_SUFFIX:-.template}"
  local output_dir="${NGINX_ENVSUBST_OUTPUT_DIR:-/etc/nginx/conf.d}"

  local template defined_envs relative_path output_path subdir
  # shellcheck disable=SC2016,SC2046
  defined_envs=$(printf '${%s} ' $(env | cut -d= -f1))
  [ -d "$template_dir" ] || return 0
  if [ ! -w "$output_dir" ]; then
    echo >&3 "$ME: ERROR: $template_dir exists, but $output_dir is not writable"
    return 0
  fi
  find "$template_dir" -follow -type f -name "*$suffix" -print | while read -r template; do
    # shellcheck disable=SC2295
    relative_path="${template#$template_dir/}"
    # shellcheck disable=SC2295
    output_path="$output_dir/${relative_path%$suffix}"
    subdir=$(dirname "$relative_path")
    # create a subdirectory where the template file exists
    mkdir -p "$output_dir/$subdir"
    echo >&3 "$ME: Running envsubst on $template to $output_path"
    envsubst "$defined_envs" < "$template" > "$output_path"
  done
}

auto_envsubst

exit 0
