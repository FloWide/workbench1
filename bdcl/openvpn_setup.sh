#!/bin/bash


mkdir -p /dev/net && \
mknod /dev/net/tun c 10 200 && \
chmod 777 /dev/net/tun

cat > /etc/openvpn/server.conf << EOF
dev tun
proto tcp-server
ifconfig 10.181.200.11 10.181.200.10
cipher AES-256-CBC
comp-lzo
keepalive 10 60
persist-key
persist-tun
user root
group root
secret /etc/openvpn/openvpn.key
route 192.168.200.0 255.255.255.0
EOF