#!/bin/bash


REALM="${SERVER}-gw"

ACCESS_TOKEN=$(curl \
    -d "client_id=admin-cli" \
    -d "username=$KEYCLOAK_ADMIN" \
    -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
    -d "grant_type=password" \
"$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" -v | jq -r .access_token)

CLIENT_ID=$(curl --header "Authorization: Bearer $ACCESS_TOKEN" "$KEYCLOAK_URL/admin/realms/$REALM/clients" -v | jq -r ' .[] | select(.clientId == "flowide").id ' )

CLIENT_SECRET=$(curl --header "Authorization: Bearer $ACCESS_TOKEN" "$KEYCLOAK_URL/admin/realms/$REALM/clients/$CLIENT_ID/client-secret" -v | jq .value)

cat > /etc/openresty/auth/oidc.lua << EOF
local CONFIG = {
    discovery = "$KEYCLOAK_URL/realms/$REALM/.well-known/openid-configuration",
    client_id = "flowide",
    client_secret = $CLIENT_SECRET,
    redirect_uri = "https://$SERVER-gw.$DOMAIN/auth_callback",
    scope = "openid email profile",
    access_token_expires_leeway = 60,
    session_contents = {access_token=true}
}

return CONFIG

EOF

exec "/usr/bin/openresty" "-g" "daemon off;"