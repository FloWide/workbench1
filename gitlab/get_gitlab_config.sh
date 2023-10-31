#!/bin/bash


REALM="${SERVER}-gw"

ACCESS_TOKEN=$(curl \
    -d "client_id=admin-cli" \
    -d "username=$KEYCLOAK_ADMIN" \
    -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
    -d "grant_type=password" \
"$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" -v | jq -r .access_token)

# echo $ACCESS_TOKEN

GITLAB_CLIENT_ID=$(curl --header "Authorization: Bearer $ACCESS_TOKEN" "$KEYCLOAK_URL/admin/realms/$REALM/clients" -v | jq -r ' .[] | select(.clientId == "gitlab").id ' )
# echo "Gitlab client id: $GITLAB_CLIENT_ID"

CLIENT_SECRET=$(curl --header "Authorization: Bearer $ACCESS_TOKEN" "$KEYCLOAK_URL/admin/realms/$REALM/clients/$GITLAB_CLIENT_ID/client-secret" -v | jq .value)
ISSUER=$(curl $KEYCLOAK_URL/realms/$REALM/.well-known/openid-configuration 2>/dev/null | jq .issuer)


# echo "Client secret: $CLIENT_SECRET"
# echo "Issuer: $ISSUER"

cat << EOF
external_url "https://$SERVER-gitlab.$DOMAIN/"

prometheus_monitoring['enable'] = false

nginx['redirect_http_to_https'] = false
nginx['listen_port'] = "80"
nginx['listen_https'] = false
sidekiq['max_concurrency'] = 10

gitlab_rails["omniauth_allow_single_sign_on"] = ["openid_connect"]
gitlab_rails["omniauth_block_auto_created_users"] = false
gitlab_rails["omniauth_providers"] = [
    {
        "name" => "openid_connect",
        "label" => "keycloak",
        "args" => {
                name: "openid_connect",
                scope: ["openid", "profile", "email"],
                response_type: "code",
                issuer:  $ISSUER,
                client_auth_method: "query",
                discovery: true,
                uid_field: "preferred_username",
                client_options: {
                    identifier: "gitlab",
                    secret: $CLIENT_SECRET,
                    redirect_uri: "https://$SERVER-gitlab.$DOMAIN/users/auth/openid_connect/callback"
              }
        }
    }
]
EOF
