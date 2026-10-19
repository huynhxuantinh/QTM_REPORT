#!/usr/bin/env python3
"""Restore Cisco IOS SSH keys after Dynamips nodes are restarted."""

from __future__ import annotations

import socket
import time


ROUTERS = (
    ("R1", "192.168.91.11", 5001),
    ("R2", "192.168.91.12", 5007),
    ("R3", "192.168.91.13", 5008),
    ("R4", "192.168.91.14", 5002),
)


def port_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def drain(connection: socket.socket) -> None:
    connection.setblocking(False)
    try:
        while connection.recv(65535):
            pass
    except (BlockingIOError, OSError):
        pass
    finally:
        connection.setblocking(True)


def send(connection: socket.socket, command: str, delay: float = 0.6) -> None:
    connection.sendall(command.encode("ascii"))
    time.sleep(delay)
    drain(connection)


def restore_ssh(name: str, host: str, console_port: int) -> None:
    if port_open(host, 22):
        print(f"{name}: SSH ready")
        return

    try:
        connection = socket.create_connection(("127.0.0.1", console_port), 2)
    except OSError:
        print(f"{name}: console not ready")
        return

    with connection:
        connection.settimeout(2)
        send(connection, "\r\n\r\n", 1)
        send(connection, "enable\r\n")
        send(connection, "configure terminal\r\n")
        send(connection, "crypto key zeroize rsa\r\n", 1)
        send(connection, "yes\r\n", 1)
        send(connection, "crypto key generate rsa modulus 1024\r\n", 7)
        send(connection, "ip ssh version 2\r\n")
        send(connection, "end\r\n")
        send(connection, "write memory\r\n", 3)

    print(f"{name}: SSH restored" if port_open(host, 22, 3) else f"{name}: retry pending")


def main() -> None:
    for router in ROUTERS:
        restore_ssh(*router)


if __name__ == "__main__":
    main()
