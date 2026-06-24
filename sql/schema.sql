-- Esquema de base de datos para el análisis de ventas de Walmart.
-- Es idempotente (IF NOT EXISTS) para poder ejecutarse de forma segura
-- tanto desde el contenedor de PostgreSQL (docker-entrypoint-initdb.d)
-- como desde la aplicación Python (app.db.init_schema).

CREATE TABLE IF NOT EXISTS sales (
    id              SERIAL PRIMARY KEY,
    store           INTEGER       NOT NULL,
    sale_date       DATE          NOT NULL,
    weekly_sales    NUMERIC(14,2) NOT NULL,
    holiday_flag    BOOLEAN       NOT NULL DEFAULT FALSE,
    temperature     NUMERIC(6,2),
    fuel_price      NUMERIC(6,3),
    cpi             NUMERIC(10,4),
    unemployment    NUMERIC(6,3),
    created_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_store_date UNIQUE (store, sale_date)
);

CREATE INDEX IF NOT EXISTS idx_sales_store ON sales (store);
CREATE INDEX IF NOT EXISTS idx_sales_date  ON sales (sale_date);
