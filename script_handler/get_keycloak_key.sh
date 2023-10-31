#!/bin/bash

REALM="${SERVER}-gw"

KEY=$(curl $KEYCLOAK_URL/realms/$REALM 2>/dev/null | jq -r .public_key)
echo -e "-----BEGIN PUBLIC KEY-----\n$KEY\n-----END PUBLIC KEY-----"