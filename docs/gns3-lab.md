# GNS3 lab

## Project

- Name: `Network_Health_Check`
- Project ID: `5efd79d8-2a84-41f6-91e6-7bae0388d9a6`
- Path: `C:\Users\ASUS\GNS3\projects\5efd79d8-2a84-41f6-91e6-7bae0388d9a6`
- Source project `Lab1_QTMNC_3600` was duplicated and remains unchanged.

## Current topology

```text
Windows browser                 Ubuntu VMware                 Cisco 3660
192.168.141.1          VMnet1   192.168.141.128      Cloud     R1 Fa0/0
       +--------------------------+---------------------+------192.168.141.11
```

Ubuntu currently receives `192.168.141.128` by DHCP. Configure it as a DHCP reservation or static address before using it as the long-running monitoring server.

The VM has two network adapters:

- `ens33` / VMnet1 Host-only: `192.168.141.128/24`, used for GNS3.
- `ens192` / NAT: `192.168.91.128/24`, used for Internet access.

The VMware files are stored at `D:\UBUNTU`. The virtual disk was expanded
from 10 GB to 30 GB on 2026-10-08; `/dev/sda1` now uses the full disk. A
pre-resize backup is available at `D:\UBUNTU-backup-before-resize-20261008`.

## R1 configuration

- Hostname: `R1`
- Management address: `192.168.141.11/24`
- Management interface: `FastEthernet0/0`, state `up/up`
- SSH: version 2, local authentication, VTY accepts SSH only
- Lab username: `admin`
- Configuration was saved with `write memory`
- IOS: `C3660-A3JK9S-M 12.4(15)T14`
- Idle-PC: `0x6076e0b4`

Credentials are intentionally not stored in this repository.

## Verification completed

```text
SSH Enabled - version 2.0
line vty 0 4
 login local
 transport input ssh
FastEthernet0/0  192.168.141.11  up  up
R1 -> Ubuntu 192.168.141.128: 5/5 ping replies, 0% loss, 59 ms average
```

## Deployment decision

Run Docker Compose inside the Ubuntu VMware VM:

```text
Ubuntu VM
├── frontend
├── backend / Netmiko
└── PostgreSQL
```

The Windows host can access the Ubuntu VM through `192.168.141.128`, while Ubuntu can access R1 through `192.168.141.11`. This avoids the Windows/uBridge loopback limitation.

Next checks inside Ubuntu:

```bash
ping -c 5 192.168.141.11
ssh admin@192.168.141.11
```

After those pass, install Docker and run the application in Ubuntu.

## Netmiko collector

The first working collector is in `backend/app/services/collectors/cisco_ios.py`.
The runnable command is installed in the Ubuntu VM at `~/QTM/backend`.

```bash
cd ~/QTM/backend
source .venv/bin/activate
python -m app.scripts.check_device
```

It collects:

- Five-minute CPU utilization.
- Processor memory pool utilization.
- Uptime and monitored interface status/error counters.
- Ubuntu-to-router management ping.
- Router-to-Ubuntu path ping with 10 packets.
- Overall `Healthy`, `Warning`, or `Critical` status.

The JSON report is written to:

```text
/home/s/QTM/backend/reports/r1-health.json
```

Live verification completed successfully on 2026-10-08. R1 returned CPU, RAM,
uptime, `FastEthernet0/0`, packet loss, and latency data. The result was
`Warning` because path latency averaged 64 ms, above the 50 ms warning threshold.

This IOS image only offers the obsolete `diffie-hellman-group1-sha1` key
exchange. The lab therefore pins Paramiko below version 4. This compatibility
setting must remain limited to the isolated GNS3 lab.

## Windows Cloud limitation

Direct host-to-R1 traffic through KM-TEST Loopback was tested but frames injected by uBridge were not delivered to the Windows TCP/IP stack. Reinstalling Npcap with **WinPcap API-compatible Mode** may repair direct Windows access, but it is no longer required for the chosen VMware architecture.

Reference: https://docs.gns3.com/docs/getting-started/installation/windows
