"""
Capa de acceso a datos (PostgreSQL).

Centraliza toda la lógica de conexión, creación de esquema, inserción y
lectura de datos. Incluye un mecanismo de reintentos (`wait_for_db`) ya que
en Docker Compose / Jenkins / CI, el contenedor de la aplicación puede
arrancar antes de que PostgreSQL esté completamente listo para aceptar
conexiones.
"""
import logging
import time
from contextlib import contextmanager
from typing import Iterable, List, Tuple

import psycopg2
from psycopg2.extras import execute_values

from app.config import get_settings

logger = logging.getLogger(__name__)


def wait_for_db(max_retries: int = 15, delay_seconds: int = 2) -> None:
    """Reintenta la conexión a PostgreSQL hasta que esté disponible."""
    settings = get_settings()
    attempt = 0
    while attempt < max_retries:
        try:
            conn = psycopg2.connect(
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password,
                dbname=settings.db_name,
            )
            conn.close()
            logger.info("Conexión a PostgreSQL establecida correctamente.")
            return
        except psycopg2.OperationalError as exc:
            attempt += 1
            logger.warning(
                "PostgreSQL no disponible (intento %s/%s): %s",
                attempt, max_retries, exc,
            )
            time.sleep(delay_seconds)
    raise ConnectionError(
        "No fue posible conectar a PostgreSQL tras varios intentos."
    )


@contextmanager
def get_connection():
    """Context manager que entrega una conexión y la cierra al finalizar."""
    settings = get_settings()
    conn = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        dbname=settings.db_name,
    )
    try:
        yield conn
    finally:
        conn.close()


def init_schema(schema_path: str = "sql/schema.sql") -> None:
    """Ejecuta el DDL de creación de tablas (idempotente: usa IF NOT EXISTS)."""
    with open(schema_path, "r", encoding="utf-8") as f:
        ddl = f.read()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()


def table_has_data() -> bool:
    """Indica si la tabla 'sales' ya contiene registros."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sales;")
            count = cur.fetchone()[0]
    return count > 0


def bulk_insert_sales(records: Iterable[Tuple]) -> int:
    """Inserta en bloque una colección de registros de ventas."""
    records = list(records)
    if not records:
        return 0

    insert_query = """
        INSERT INTO sales
            (store, sale_date, weekly_sales, holiday_flag,
             temperature, fuel_price, cpi, unemployment)
        VALUES %s
        ON CONFLICT (store, sale_date) DO NOTHING
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_query, records)
        conn.commit()
    return len(records)


def fetch_all_sales() -> List[Tuple]:
    """Recupera todos los registros de ventas almacenados."""
    query = """
        SELECT store, sale_date, weekly_sales, holiday_flag,
               temperature, fuel_price, cpi, unemployment
        FROM sales
        ORDER BY sale_date;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    return rows
