"""
Módulo de configuración centralizada de la aplicación.

Lee la configuración desde variables de entorno, lo que permite que la misma
imagen Docker funcione en distintos entornos (local, Jenkins, Travis CI,
Codeship, producción) sin modificar código.
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    csv_path: str


def get_settings() -> Settings:
    """Construye un objeto Settings a partir de variables de entorno."""
    return Settings(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_user=os.getenv("DB_USER", "walmart_user"),
        db_password=os.getenv("DB_PASSWORD", "walmart_pass"),
        db_name=os.getenv("DB_NAME", "walmart_sales"),
        csv_path=os.getenv("CSV_PATH", "data/Walmart_Sales.csv"),
    )
