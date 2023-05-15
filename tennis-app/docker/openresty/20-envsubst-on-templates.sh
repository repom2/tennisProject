#!/bin/sh

# From:
# https://raw.githubusercontent.com/nginxinc/docker-nginx/master/stable/debian/20-envsubst-on-templates.sh

set -e

ME=$(basename "${0}")

export OIDC_SCOPE="${OIDC_SCOPE:-openid email profile}"
export NGINX_PROXY_CONNECT_TIMEOUT="${NGINX_PROXY_CONNECT_TIMEOUT:-60s}"
export NGINX_PROXY_READ_TIMEOUT="${NGINX_PROXY_READ_TIMEOUT:-60s}"
export NGINX_PROXY_SEND_TIMEOUT="${NGINX_PROXY_SEND_TIMEOUT:-60s}"

if [ -z "${SESSION_SECRET}" ]; then
	echo "SESSION_SECRET is not set, generating random"
	export SESSION_SECRET=$(openssl rand -hex 32)
fi

auto_envsubst() {
	local template_dir="${NGINX_ENVSUBST_TEMPLATE_DIR:-/etc/nginx/templates}"
	local suffix="${NGINX_ENVSUBST_TEMPLATE_SUFFIX:-.template}"
	local output_dir="${NGINX_ENVSUBST_OUTPUT_DIR:-/etc/nginx/conf.d}"

	local template defined_envs relative_path output_path subdir
	defined_envs=$(printf '${%s} ' $(env | cut -d= -f1))
	[ -d "$template_dir" ] || return 0
	if [ ! -w "$output_dir" ]; then
		echo >&3 "$ME: ERROR: $template_dir exists, but $output_dir is not writable"
		return 0
	fi
	find "$template_dir" -follow -type f -name "*$suffix" -print | while read -r template; do
		relative_path="${template#$template_dir/}"
		output_path="$output_dir/${relative_path%$suffix}"
		subdir=$(dirname "$relative_path")
		# create a subdirectory where the template file exists
		mkdir -p "$output_dir/$subdir"
		echo >&3 "$ME: Running envsubst on $template to $output_path"
		envsubst "$defined_envs" <"$template" >"$output_path"
	done
}

auto_envsubst

exit 0
