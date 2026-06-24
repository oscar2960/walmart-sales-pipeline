"""
Pruebas unitarias del módulo de métricas de negocio.

Trabajan sobre tuplas en memoria (sin base de datos), lo que permite que
esta suite se ejecute en cualquier entorno de CI sin necesidad de
levantar PostgreSQL.
"""
from datetime import date

from app import metrics

SAMPLE_RECORDS = [
    (1, date(2010, 2, 5), 1000.0, False, 40.0, 2.5, 210.0, 8.0),
    (1, date(2010, 2, 12), 2000.0, True, 38.0, 2.5, 211.0, 8.0),
    (2, date(2010, 2, 5), 3000.0, False, 40.0, 2.6, 210.5, 8.3),
    (2, date(2010, 3, 5), 1500.0, False, 45.0, 2.6, 210.8, 8.3),
]


def test_total_sales():
    assert metrics.total_sales(SAMPLE_RECORDS) == 7500.0


def test_sales_by_store():
    result = metrics.sales_by_store(SAMPLE_RECORDS)
    assert result[1] == 3000.0
    assert result[2] == 4500.0


def test_average_sales_by_store():
    result = metrics.average_sales_by_store(SAMPLE_RECORDS)
    assert result[1] == 1500.0
    assert result[2] == 2250.0


def test_best_and_worst_store():
    best_store, best_value = metrics.best_store(SAMPLE_RECORDS)
    worst_store, worst_value = metrics.worst_store(SAMPLE_RECORDS)
    assert best_store == 2
    assert best_value == 4500.0
    assert worst_store == 1
    assert worst_value == 3000.0


def test_holiday_vs_regular():
    result = metrics.holiday_vs_regular(SAMPLE_RECORDS)
    assert result["holiday_total"] == 2000.0
    assert result["regular_total"] == 5500.0
    assert result["holiday_avg"] == 2000.0
    assert result["regular_avg"] == round(5500.0 / 3, 2)


def test_monthly_sales():
    result = metrics.monthly_sales(SAMPLE_RECORDS)
    assert result["2010-02"] == 6000.0
    assert result["2010-03"] == 1500.0


def test_empty_records_do_not_raise():
    assert metrics.total_sales([]) == 0.0
    store, value = metrics.best_store([])
    assert store is None
    assert value == 0.0
    assert metrics.sales_by_store([]) == {}
    assert metrics.monthly_sales([]) == {}
