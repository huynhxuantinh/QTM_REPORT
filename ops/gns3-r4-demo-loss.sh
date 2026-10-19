#!/usr/bin/env bash
set -euo pipefail

INTERFACE="veth-br"
R4_IP="192.168.91.14"

disable_loss() {
    tc qdisc del dev "$INTERFACE" root 2>/dev/null || true
}

enable_loss() {
    disable_loss
    tc qdisc add dev "$INTERFACE" root handle 1: prio bands 3
    tc qdisc add dev "$INTERFACE" parent 1:3 handle 30: netem loss 5% seed 3
    tc filter add dev "$INTERFACE" protocol ip parent 1:0 prio 3 u32 \
        match ip dst "$R4_IP"/32 \
        match ip protocol 1 0xff \
        flowid 1:3
}

case "${1:-status}" in
    on)
        enable_loss
        echo "R4 packet-loss demo: ON"
        ;;
    off)
        disable_loss
        echo "R4 packet-loss demo: OFF"
        ;;
    status)
        tc qdisc show dev "$INTERFACE"
        ;;
    *)
        echo "Usage: $0 {on|off|status}" >&2
        exit 2
        ;;
esac
