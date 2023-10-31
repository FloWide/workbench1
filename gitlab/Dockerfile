ARG GITLAB_VERSION
FROM gitlab/gitlab-ce:${GITLAB_VERSION}

ARG HTTPS_PROXY=""
ARG HTTP_PROXY=""
RUN apt-get update && apt-get -y install unzip curl jq

COPY . .

ENV GITLAB_POST_RECONFIGURE_SCRIPT="gitlab-rails runner /setup.rb"

CMD ./get_gitlab_config.sh > /etc/gitlab/gitlab.rb && /assets/wrapper