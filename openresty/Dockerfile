FROM openresty/openresty

ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
RUN apt update && apt install -y curl perl jq openresty-opm openvpn && \
    opm install zmartzone/lua-resty-openidc=1.7.5 ledgetech/lua-resty-http=0.16.1 bungle/lua-resty-session=3.10 cdbattags/lua-resty-jwt=0.2.0

COPY ./auth/ /etc/openresty/auth/
COPY 502.html /etc/openresty/error/


COPY docker_entrypoint.sh .


ENTRYPOINT [ "./docker_entrypoint.sh" ]
