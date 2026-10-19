#!/usr/bin/env bash
set -euo pipefail

BRIDGE="br-gns3"
BRIDGE_IP="192.168.91.1/24"
BRIDGE_END="veth-br"
GNS3_END="veth-gns3"

ip link show "$BRIDGE" >/dev/null 2>&1 || ip link add "$BRIDGE" type bridge
ip addr replace "$BRIDGE_IP" dev "$BRIDGE"
ip link set "$BRIDGE" up

if ! ip link show "$BRIDGE_END" >/dev/null 2>&1; then
    ip link add "$BRIDGE_END" type veth peer name "$GNS3_END"
fi

ip link set "$BRIDGE_END" master "$BRIDGE"
ip link set "$BRIDGE_END" up
ip link set "$GNS3_END" up

# uBridge captures packets before checksum offload is completed. Disabling
# offload prevents IOS from dropping TCP/SSH packets with invalid checksums.
ethtool -K "$BRIDGE_END" tx off tso off gso off gro off >/dev/null 2>&1 || true
ethtool -K "$GNS3_END" tx off tso off gso off gro off >/dev/null 2>&1 || true

sysctl -w net.ipv4.ip_forward=1 >/dev/null
