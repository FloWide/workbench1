#!/bin/bash


set -e

function sigterm_handler() {
    echo "SIGTERM signal received,shutting down..."
    kill $(cat /var/run/scl.pid)
}

SCL_EXEC=$(find . -name "scl*" | grep -v "strip")
SCL_STRIP_EXEC=$(find . -name "scl*strip" )

echo "Found SCL executable(s): $SCL_EXEC , $SCL_STRIP_EXEC"


if [ -z "$SCL_STRIP" ]; then
    SCL=$SCL_EXEC
else
    SCL=$SCL_STRIP_EXEC
fi

echo "Running SCL with executable $SCL"

eval "$SCL --port $SCL_PORT --inputmbruuid=$SCL_INPUT_MBR_UUID --posmbruuid=$SCL_POS_MBR_UUID --tracelog" & >> /dev/stdout
echo $! > /var/run/scl.pid

./webhook.sh

trap "sigterm_handler; exit" TERM

wait