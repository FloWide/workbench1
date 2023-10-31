FROM nginx:stable-alpine

ARG HTTPS_PROXY=""
ARG HTTP_PROXY=""

RUN apk --no-cache add curl jq unzip bash

WORKDIR /app

COPY . .

ARG WORKBENCH_VERSION="latest"



RUN ./get_package.sh -o FloWide -r workbench-ui -f release_files.zip -v ${WORKBENCH_VERSION} && \
    unzip release_files.zip && \
    cp -a ./dist/flowide-ui/. /usr/share/nginx/html && \
    rm -f release_files.zip && rm -rf ./dist
ARG SERVER
ARG DOMAIN
RUN ./config.sh

HEALTHCHECK --interval=1m --timeout=30s --start-period=5s --retries=3 \
            CMD curl -f http://localhost/ || exit 1