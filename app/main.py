"""
Punto de entrada de la aplicación.

Orquesta el flujo completo: espera la disponibilidad de PostgreSQL, crea el
esquema, ejecuta el ETL (si la tabla está vacía), calcula métricas y
muestra un reporte de ventas por consola.
"""
import logging
import sys

from app import db, etl, metrics
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def print_header(title: str) -> None:
    print("\n" + "=" * 64)
    print(title.center(64))
    print("=" * 64)


def run() -> int:
    settings = get_settings()

    logger.info("Esperando disponibilidad de PostgreSQL en %s:%s ...",
                settings.db_host, settings.db_port)
    db.wait_for_db()

    logger.info("Inicializando esquema de base de datos...")
    db.init_schema()

    if not db.table_has_data():
        logger.info("Cargando datos desde: %s", settings.csv_path)
        raw_df = etl.read_csv(settings.csv_path)
        clean_df = etl.transform(raw_df)
        records_to_insert = etl.to_records(clean_df)
        inserted = db.bulk_insert_sales(records_to_insert)
        logger.info("%s registros procesados e insertados.", inserted)
    else:
        logger.info("La tabla 'sales' ya contiene datos. Se omite la carga inicial.")

    logger.info("Calculando métricas de negocio...")
    records = db.fetch_all_sales()

    if not records:
        logger.warning("No hay registros en la base de datos para analizar.")
        return 1

    print_header("REPORTE DE VENTAS - WALMART")
    print(f"Total de registros analizados : {len(records)}")
    print(f"Ventas totales                : $ {metrics.total_sales(records):,.2f}")

    best_store_id, best_value = metrics.best_store(records)
    worst_store_id, worst_value = metrics.worst_store(records)
    print(f"Tienda con mejores ventas      : #{best_store_id}  ($ {best_value:,.2f})")
    print(f"Tienda con peores ventas       : #{worst_store_id}  ($ {worst_value:,.2f})")

    print_header("VENTAS TOTALES POR TIENDA (TOP 5)")
    for store, total in list(metrics.sales_by_store(records).items())[:5]:
        print(f"  Tienda #{store:<5} -> $ {total:,.2f}")

    print_header("PROMEDIO SEMANAL DE VENTAS POR TIENDA (TOP 5)")
    avg_by_store = metrics.average_sales_by_store(records)
    top_avg = sorted(avg_by_store.items(), key=lambda x: x[1], reverse=True)[:5]
    for store, avg in top_avg:
        print(f"  Tienda #{store:<5} -> $ {avg:,.2f}")

    print_header("VENTAS: SEMANA FERIADO VS. SEMANA REGULAR")
    hv = metrics.holiday_vs_regular(records)
    print(f"  Promedio en semana feriado  : $ {hv['holiday_avg']:,.2f}")
    print(f"  Promedio en semana regular  : $ {hv['regular_avg']:,.2f}")
    print(f"  Total en semanas feriado    : $ {hv['holiday_total']:,.2f}")
    print(f"  Total en semanas regulares  : $ {hv['regular_total']:,.2f}")

    print_header("TENDENCIA MENSUAL DE VENTAS")
    for month, total in metrics.monthly_sales(records).items():
        print(f"  {month} -> $ {total:,.2f}")

    print("\n✅ Proceso de análisis finalizado con éxito.\n")
    return 0


if __name__ == "__main__":
    sys.exit(run())
