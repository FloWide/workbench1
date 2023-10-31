FROM python:3.6.15-slim-bullseye

ARG HTTPS_PROXY=""
ARG HTTP_PROXY=""
RUN apt update && \
    apt install -y curl jq unzip

WORKDIR /app

COPY . .

ARG DCM_VERSION="latest"


RUN ./get_package.sh -o FloWide -r dcm1 -f release.zip -v ${DCM_VERSION} && \
    unzip release.zip && \
    mv ./dist/* . && \
    rm -f release.zip && rm -rf ./dist

ENV DCM_PORT=80
ENV DCM_LOG_LEVEL=debug
ENV DCM_SAVE_INTERVAL=01:00:00
ENV DCM_KEEP_INTERVAL=24:00:00
ENV DCM_STORAGE_FILE=/usr/dcm/database.db
ENV REDIS_HOST=bdcl
ENV DCM_TRANSLATOR_MODULES='[]'
ENTRYPOINT [ "./docker_entrypoint.sh"]

EXPOSE ${DCM_PORT}

HEALTHCHECK --interval=1m --timeout=30s --start-period=5s --retries=3 \
            CMD curl http://localhost/v2 || exit 1