FROM debian:10

ARG HTTPS_PROXY=""
ARG HTTP_PROXY=""
RUN apt update && apt install -y curl jq unzip openvpn bash redis python3 ntp

WORKDIR /app

COPY . .

ARG BDCL_VERSION="latest"


ENV LOLAN_VARS_DIR="./lolan-vars"
RUN ./get_package.sh -o FloWide -r bdcl1 -f release.zip -v ${BDCL_VERSION} && \
    ./get_package.sh -o FloWide -r bdcl1 -f lolan-vars.zip -v ${BDCL_VERSION} && \
    unzip lolan-vars.zip && \
    unzip release.zip && \
    mv ./dist/* . && \
    rm -f release.zip && rm -rf ./dist

RUN ./openvpn_setup.sh

RUN echo "disable kernel" >> /etc/ntp.conf

ENV BDCL_PORT=80
ENV REDIS_PORT=6379
ENV OPENVPN_PORT=1194
ENV BDCL_LOG_LEVEL=debug
ENV CU_MANAGEMENT_PORT=50002
ENV CU_FPGA_PORT=50001
ENV PYTHONUNBUFFERED=1
ENTRYPOINT [ "./docker_entrypoint.sh" ]

EXPOSE $BDCL_PORT
EXPOSE $REDIS_PORT
EXPOSE $OPENVPN_PORT
