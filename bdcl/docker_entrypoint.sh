#!/bin/bash

set -e


function sigterm_handler() {
    echo "SIGTERM signal received,shutting down..."
    kill $(cat /var/run/openvpn.pid)
    kill $(cat /var/run/redis.pid)
    kill $(cat /var/run/bdcl.pid)
}

BDCL_EXEC=$(find . -name "bdcl*" | grep -v "strip")
BDCL_STRIP_EXEC=$(find . -name "bdcl*strip" )

echo "Found BDCL executable(s): $BDCL_EXEC , $BDCL_STRIP_EXEC"

echo "Starting redis server..."
redis-server --daemonize yes --port $REDIS_PORT --protected-mode no --bind 0.0.0.0

echo "Starting openvpn server..."
openvpn --config /etc/openvpn/server.conf --daemon --port $OPENVPN_PORT
echo $! >> /var/run/openvpn.pid


python3 udp_listener.py CU_MANAGEMENT $CU_MANAGEMENT_PORT & > /dev/stdout
python3 udp_listener.py CU_FPGA $CU_FPGA_PORT & > /dev/stdout

echo "Starting ntpd..."
ntpd

if [ -z "$BDCL_STRIP" ]; then
    BDCL=$BDCL_EXEC
else
    BDCL=$BDCL_STRIP_EXEC
fi

echo "Running BDCL with executable $BDCL"

eval "$BDCL --log-level $BDCL_LOG_LEVEL --lolan-var-dir $LOLAN_VARS_DIR --rest $BDCL_PORT --max-buffering-microsec 500000 --overflow-duration-microsec 900000 --device-timeout-minutes 60 --udp-message-timeout-seconds 3 --lolan-id 1 --ntp-difference-duration-warning-microsec 10000 --ack-channel-uuid 451513e9-da18-4c35-863c-877bac283869   " \
      & > /dev/stdout  
echo $! > /var/run/bdcl.pid

trap "sigterm_handler; exit" TERM

wait 