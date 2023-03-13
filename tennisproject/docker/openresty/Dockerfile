FROM openresty/openresty:1.21.4.1-0-bullseye-fat

# OIDC
# 1.7.5 needs lua-resty-session 4 and it does not seem to work at the moment
RUN opm get zmartzone/lua-resty-openidc=1.7.4 bungle/lua-resty-session=3.10 \
    && mkdir /docker-entrypoint.d

COPY ./docker-entrypoint.sh /
COPY ./20-envsubst-on-templates.sh /docker-entrypoint.d
COPY ./apigw.conf.template /etc/nginx/templates/default.conf.template

# Expose port
EXPOSE 80

CMD ["/usr/bin/openresty", "-g", "daemon off;"]
ENTRYPOINT ["/docker-entrypoint.sh"]
