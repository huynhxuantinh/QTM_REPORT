from __future__ import annotations

from pathlib import Path

import yaml
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent


def test_base_migration_builds_devices_table(tmp_path: Path) -> None:
    database_path = (tmp_path / "migration.db").as_posix()
    database_url = f"sqlite+pysqlite:///{database_path}"
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    inspector = inspect(create_engine(database_url))
    assert {
        "devices",
        "health_checks",
        "interface_results",
        "ping_results",
        "health_findings",
    }.issubset(inspector.get_table_names())
    assert "uq_devices_active_host_port" in {
        index["name"] for index in inspector.get_indexes("devices")
    }


def test_compose_defines_healthy_backend_and_postgres() -> None:
    compose_path = PROJECT_ROOT / "docker-compose.yml"
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    assert {"backend", "db"}.issubset(compose["services"])
    assert compose["services"]["db"]["healthcheck"]
    assert compose["services"]["backend"]["depends_on"]["db"] == {
        "condition": "service_healthy"
    }
    assert "postgresql+psycopg://" in compose["services"]["backend"][
        "environment"
    ]["DATABASE_URL"]
    assert compose["services"]["db"]["volumes"] == [
        "postgres_data:/var/lib/postgresql/data"
    ]

