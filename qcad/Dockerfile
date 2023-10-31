FROM debian:10
ARG HTTPS_PROXY=""
ARG HTTP_PROXY=""
RUN apt-get update && apt-get install -y curl libglib2.0 libgl-dev libxrender-dev libfontconfig
WORKDIR /opt
RUN curl -s https://cloud.flowide.net/index.php/s/T24nBHTN2f8RPtG/download --output qcad.tar.gz && tar xzf qcad.tar.gz && ln -s qcad-3.27.1-pro-linux-x86_64 qcad
WORKDIR /opt/qcad
