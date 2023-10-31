#!/bin/bash

curl_opts=(
    -s
    -o /dev/null
    -w ''%{http_code}''
    --header "X-Webhook-Secret: $WEBHOOK_SECRET"
    --header "Content-Type: application/json"
    -d ${WEBHOOK_DATA:-'{}'}
)
echo "Sending init webhook..."
RESPONSE_CODE=$(curl "${curl_opts[@]}" "$WEBHOOK_URL")
echo $RESPONSE_CODE

if [ $RESPONSE_CODE -ge 200 ] && [ $RESPONSE_CODE -lt 300 ]; then
    echo "Init webhook succeded"
    exit 0
else
    echo "Init webhook failed. Exiting..."
    exit 1
fi