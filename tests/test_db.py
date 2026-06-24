"""
Pruebas de integración con PostgreSQL.

Estas pruebas SÍ requieren una base de datos real disponible (la que se
levanta vía Docker Compose, Travis CI, Codeship o Jenkins). Si no hay una
instancia de PostgreSQL accesible en DB_HOST:DB_PORT, se omiten
automáticamente (skip) en lugar de fallar, para no romper la ejecución de
la suite de pruebas unitarias en entornos sin base de datos.
"""
import socket

import pytest

from app import db
from app.config import get_settings


def _db_available() -> bool:
    settings = get_settings()
    try:
        with socket.create_connection((settings.db_host, settings.db_port), timeout=2):
            return True
    except OSError:
        return False


requires_db = pytest.mark.skipif(
    not _db_available(),
    reason="PostgreSQL no disponible en este entorno (prueba de integración).",
)


@requires_db
def test_wait_for_db_succeeds():
    db.wait_for_db(max_retries=3, delay_seconds=1)


@requires_db
def test_schema_initialization_is_idempotent():
    db.init_schema()
    db.init_schema()  # ejecutar dos veces no debe fallar (usa IF NOT EXISTS)
    assert isinstance(db.table_has_data(), bool)


@requires_db
def test_bulk_insert_and_fetch_roundtrip():
    from datetime import date

    db.init_schema()
    sample = [(999, date(2099, 1, 1), 1234.56, False, 50.0, 3.0, 200.0, 7.0)]
    db.bulk_insert_sales(sample)

    rows = db.fetch_all_sales()
    match = [r for r in rows if r[0] == 999 and r[1] == date(2099, 1, 1)]
    assert len(match) == 1
    assert match[0][2] == 1234.56
