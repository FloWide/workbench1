#!/bin/bash

set -e


echo "Getting keyloak public key"
./get_keycloak_key.sh > /app/keycloak.key
cat /app/keycloak.key

# Try to wait until gitlab admin token is usable or bail
echo "Trying Gitlab admin token"
timeout 120s bash -c 'while [[ $(curl -s -o /dev/null -w ''%{http_code}'' --header "Authorization: Bearer '$GITLAB_ADMIN_TOKEN'" "'$GITLAB_URL'/api/v4/users?per_page=1") != "200" ]]; do sleep 2; done;' || exit 1




python -m script_handler --git-service-url $GITLAB_URL \
                   --git-service-token $GITLAB_ADMIN_TOKEN \
                   --git-hook-secret $GITLAB_SYSTEM_HOOK_SECRET \
                   --auth-secret /app/keycloak.key \
                   --repos-root /data/script_handler/repos \
                   --run-dir /data/script_handler/releases \
                   --venv-activator "${VENV}/bin/activate" \
                   --streamlit-ports 17001 17102 \
                   --port $SCRIPT_HANDLER_PORT \
                   --log-level $SCRIPT_HANDLER_LOG_LEVEL \
                   --enable-lsp \
                   --webhooks-secret $WEBHOOK_SECRET
