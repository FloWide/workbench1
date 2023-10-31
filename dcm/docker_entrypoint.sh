#!/bin/bash

set -e

function sigterm_handler() {
    echo "SIGTERM signal received,shutting down..."
    kill $(cat /var/run/dcm.pid)
}

DCM_EXEC=$(find . -name "dcm*" | grep --invert-match "strip")
DCM_STRIP_EXEC=$(find . -name "dcm*strip" )

echo "Found DCM executable(s): $DCM_EXEC , $DCM_STRIP_EXEC"

if [ -z "$DCM_STRIP" ]; then
    DCM=$DCM_EXEC
else
    DCM=$DCM_STRIP_EXEC
fi

echo "Running DCM with executable $DCM"
eval "$DCM --translator /app/translator/translator.py  --port ${DCM_PORT} -c -l ${DCM_LOG_LEVEL}  -s '-f ${DCM_STORAGE_FILE} -i ${DCM_SAVE_INTERVAL} -k ${DCM_KEEP_INTERVAL}' " & >> /dev/stdout
echo $! > /var/run/dcm.pid

./webhook.sh

trap "sigterm_handler; exit" TERM

wait