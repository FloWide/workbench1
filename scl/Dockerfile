FROM debian:10

ARG HTTPS_PROXY=""
ARG HTTP_PROXY=""
RUN apt update && apt install -y curl jq unzip


WORKDIR /app

COPY . .


ARG SCL_VERSION="latest"



RUN ./get_package.sh -o FloWide -r scl1 -f release.zip -v ${SCL_VERSION} && \
    unzip release.zip && \
    mv ./dist/* . && \
    rm -f release.zip && rm -rf ./dist


ENV SCL_PORT=80
ENV SCL_INPUT_MBR_UUID="451513e9-da18-4c35-863c-877bac283861"
ENV SCL_POS_MBR_UUID="451513e9-da18-4c35-863c-877bac283863"
ENV REDIS_HOST=bdcl
ENV REDIS_PORT=6379
ENTRYPOINT [ "./docker_entrypoint.sh" ]

HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 CMD [ "/app/no_pos_timeout.sh" ]

EXPOSE ${SCL_PORT}