"""
Módulo ETL (Extract, Transform, Load) - capa de Ingeniería de Datos.

- Extract: lectura del archivo CSV de ventas.
- Transform: limpieza de tipos, parseo de fechas, eliminación de duplicados.
- Load: conversión a una estructura de tuplas lista para insertar en
  PostgreSQL (la inserción real ocurre en app.db).
"""
import logging
from typing import List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "Store",
    "Date",
    "Weekly_Sales",
    "Holiday_Flag",
    "Temperature",
    "Fuel_Price",
    "CPI",
    "Unemployment",
]


def read_csv(csv_path: str) -> pd.DataFrame:
    """Lee el archivo Walmart_Sales.csv y valida que tenga las columnas
    esperadas según el dataset público de Kaggle 'Walmart Sales'."""
    df = pd.read_csv(csv_path)
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes en el CSV: {sorted(missing)}")
    logger.info("CSV leído correctamente: %s filas, %s columnas", *df.shape)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica transformaciones básicas de limpieza y tipado."""
    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    df = df.dropna(subset=["Date", "Store", "Weekly_Sales"])

    df["Store"] = df["Store"].astype(int)
    df["Holiday_Flag"] = df["Holiday_Flag"].astype(int).astype(bool)
    df["Weekly_Sales"] = df["Weekly_Sales"].astype(float).round(2)

    for col in ("Temperature", "Fuel_Price", "CPI", "Unemployment"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.drop_duplicates(subset=["Store", "Date"])
    removed = before - len(df)
    if removed:
        logger.info("Se eliminaron %s registros duplicados (Store, Date).", removed)

    return df.reset_index(drop=True)


def to_records(df: pd.DataFrame) -> List[Tuple]:
    """Convierte el DataFrame limpio en una lista de tuplas para inserción
    masiva en PostgreSQL."""
    records: List[Tuple] = []
    for _, row in df.iterrows():
        records.append(
            (
                int(row["Store"]),
                row["Date"].date(),
                float(row["Weekly_Sales"]),
                bool(row["Holiday_Flag"]),
                float(row["Temperature"]) if pd.notna(row.get("Temperature")) else None,
                float(row["Fuel_Price"]) if pd.notna(row.get("Fuel_Price")) else None,
                float(row["CPI"]) if pd.notna(row.get("CPI")) else None,
                float(row["Unemployment"]) if pd.notna(row.get("Unemployment")) else None,
            )
        )
    return records
