FROM openresty/openresty:1.19.9.1-12-bullseye-fat

# OIDC
RUN opm install zmartzone/lua-resty-openidc \
    && mkdir /docker-entrypoint.d

COPY docker/openresty/docker-entrypoint.sh /
COPY docker/openresty/20-envsubst-on-templates.sh /docker-entrypoint.d

# Expose port
EXPOSE 80

CMD ["/usr/bin/openresty", "-g", "daemon off;"]
ENTRYPOINT ["/docker-entrypoint.sh"]
