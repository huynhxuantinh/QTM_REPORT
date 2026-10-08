from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path

from app.domain.models import DeviceConfig
from app.services.collectors.cisco_ios import CiscoIosCollector


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect health metrics from a Cisco IOS router."
    )
    parser.add_argument("--name", default=os.getenv("ROUTER_NAME", "R1"))
    parser.add_argument(
        "--host",
        default=os.getenv("ROUTER_HOST", "192.168.141.11"),
    )
    parser.add_argument(
        "--username",
        default=os.getenv("ROUTER_USERNAME", "admin"),
    )
    parser.add_argument("--password", default=os.getenv("ROUTER_PASSWORD"))
    parser.add_argument(
        "--target",
        default=os.getenv("PING_TARGET", "192.168.141.128"),
    )
    parser.add_argument(
        "--interfaces",
        default=os.getenv("MONITORED_INTERFACES", "FastEthernet0/0"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/r1-health.json"),
    )
    args = parser.parse_args()

    password = args.password or getpass.getpass("Router password: ")
    monitored_interfaces = tuple(
        item.strip() for item in args.interfaces.split(",") if item.strip()
    )
    config = DeviceConfig(
        name=args.name,
        host=args.host,
        username=args.username,
        password=password,
        monitored_interfaces=monitored_interfaces,
        path_ping_target=args.target or None,
    )
    report = CiscoIosCollector().collect(config)
    payload = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(f"{payload}\n", encoding="utf-8")
    print(payload)
    print(f"\nReport saved to: {args.output.resolve()}")
    return 0 if report.status != "Critical" else 2


if __name__ == "__main__":
    raise SystemExit(main())

