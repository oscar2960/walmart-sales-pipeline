"""
Módulo de métricas de negocio.

Recibe registros de ventas (tuplas con el orden definido en app.db) y
calcula indicadores simples solicitados por el caso de negocio: ventas
totales, ranking de tiendas, comparación feriado vs. día regular y
tendencia mensual.

Se trabaja sobre tuplas planas (no DataFrame) para que estas funciones
puedan probarse unitariamente sin depender de pandas ni de una conexión
real a base de datos.
"""
from collections import defaultdict
from typing import Dict, List, Tuple

Record = Tuple  # (store, sale_date, weekly_sales, holiday_flag, temp, fuel, cpi, unemployment)


def total_sales(records: List[Record]) -> float:
    return round(sum(r[2] for r in records), 2)


def sales_by_store(records: List[Record]) -> Dict[int, float]:
    totals: Dict[int, float] = defaultdict(float)
    for r in records:
        totals[r[0]] += float(r[2])
    ordered = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return {store: round(total, 2) for store, total in ordered}


def average_sales_by_store(records: List[Record]) -> Dict[int, float]:
    totals: Dict[int, float] = defaultdict(float)
    counts: Dict[int, int] = defaultdict(int)
    for r in records:
        totals[r[0]] += float(r[2])
        counts[r[0]] += 1
    return {store: round(totals[store] / counts[store], 2) for store in totals}


def best_store(records: List[Record]):
    totals = sales_by_store(records)
    if not totals:
        return None, 0.0
    return max(totals.items(), key=lambda x: x[1])


def worst_store(records: List[Record]):
    totals = sales_by_store(records)
    if not totals:
        return None, 0.0
    return min(totals.items(), key=lambda x: x[1])


def holiday_vs_regular(records: List[Record]) -> Dict[str, float]:
    holiday_total = regular_total = 0.0
    holiday_count = regular_count = 0
    for r in records:
        if r[3]:
            holiday_total += float(r[2])
            holiday_count += 1
        else:
            regular_total += float(r[2])
            regular_count += 1
    return {
        "holiday_avg": round(holiday_total / holiday_count, 2) if holiday_count else 0.0,
        "regular_avg": round(regular_total / regular_count, 2) if regular_count else 0.0,
        "holiday_total": round(holiday_total, 2),
        "regular_total": round(regular_total, 2),
    }


def monthly_sales(records: List[Record]) -> Dict[str, float]:
    totals: Dict[str, float] = defaultdict(float)
    for r in records:
        key = r[1].strftime("%Y-%m")
        totals[key] += float(r[2])
    return {k: round(v, 2) for k, v in sorted(totals.items())}
