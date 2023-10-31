
FROM python:3.10.6-slim-bullseye

ARG HTTPS_PROXY=""
ARG HTTP_PROXY=""
ARG SCRIPT_HANDLER_VERSION="latest"
RUN apt-get update && apt-get -y install unzip curl jq libpq-dev gcc git libgomp1 libgl1-mesa-glx python3-opencv libzbar0 libgdal-dev build-essential && \
    curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get -y install nodejs && \
    npm install -g typescript rollup 

WORKDIR /app

COPY . .

ENV VENV='/app/streamlit-venv'
RUN ./get_package.sh -o FloWide -r scripthandler -f streamlit-venv-builder.zip -v ${SCRIPT_HANDLER_VERSION} && \
    unzip streamlit-venv-builder.zip && \
    cd streamlit-venv-builder && \
    ./get_extra_packages.sh && ./build-env.sh && \
    $VENV/bin/pip install pygdal==$(gdal-config --version).* && \
    cd .. && rm -f streamlit-venv-builder.zip && rm -rf streamlit-venv-builder

RUN ./get_package.sh -o FloWide -r scripthandler -f release.zip -v ${SCRIPT_HANDLER_VERSION} && \
    unzip release.zip && \
    find ./dist -name "*.whl" | xargs --no-run-if-empty pip install && \
    rm -f release.zip && rm -rf ./dist

ENV SCRIPT_HANDLER_PORT=80
ENV SCRIPT_HANDLER_LOG_LEVEL="DEBUG"
ENV GITLAB_SYSTEM_HOOK_SECRET=""
ENV WEBHOOK_SECRET=""

ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_RUN_ON_SAVE=true

ENTRYPOINT [ "./docker_entrypoint.sh" ]

EXPOSE $SCRIPT_HANDLER_PORT

HEALTHCHECK --interval=1m --timeout=30s --start-period=5s --retries=3 \
            CMD curl http://localhost/repo || exit 1
