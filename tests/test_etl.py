"""
Pruebas unitarias del módulo ETL.

No requieren base de datos: trabajan sobre CSVs temporales en disco
(tmp_path) y sobre DataFrames en memoria.
"""
import pandas as pd
import pytest

from app import etl

SAMPLE_CSV = """Store,Date,Weekly_Sales,Holiday_Flag,Temperature,Fuel_Price,CPI,Unemployment
1,05-02-2010,1643690.90,0,42.31,2.572,211.0963582,8.106
1,12-02-2010,1641957.44,1,38.51,2.548,211.2421698,8.106
2,05-02-2010,2136989.46,0,40.06,2.625,210.7501,8.324
1,05-02-2010,1643690.90,0,42.31,2.572,211.0963582,8.106
"""


@pytest.fixture
def sample_df():
    from io import StringIO
    return pd.read_csv(StringIO(SAMPLE_CSV))


def test_read_csv_raises_when_columns_missing(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("Store,Date\n1,05-02-2010\n")
    with pytest.raises(ValueError):
        etl.read_csv(str(bad_csv))


def test_read_csv_ok(tmp_path):
    csv_file = tmp_path / "good.csv"
    csv_file.write_text(SAMPLE_CSV)
    df = etl.read_csv(str(csv_file))
    assert len(df) == 4
    assert "Weekly_Sales" in df.columns


def test_transform_removes_duplicates(sample_df):
    result = etl.transform(sample_df)
    # La fila (Store=1, Date=05-02-2010) está duplicada en el CSV de muestra
    assert len(result) == 3


def test_transform_types(sample_df):
    result = etl.transform(sample_df)
    assert result["Store"].dtype == int
    assert result["Holiday_Flag"].dtype == bool
    assert str(result["Date"].dtype).startswith("datetime64")


def test_transform_drops_invalid_dates():
    df = pd.DataFrame({
        "Store": [1, 2],
        "Date": ["05-02-2010", "fecha-invalida"],
        "Weekly_Sales": [1000.0, 2000.0],
        "Holiday_Flag": [0, 0],
        "Temperature": [40.0, 41.0],
        "Fuel_Price": [2.5, 2.5],
        "CPI": [210.0, 210.0],
        "Unemployment": [8.0, 8.0],
    })
    result = etl.transform(df)
    assert len(result) == 1


def test_to_records_structure(sample_df):
    clean = etl.transform(sample_df)
    records = etl.to_records(clean)
    assert isinstance(records, list)
    assert len(records) == len(clean)
    store, sale_date, weekly_sales, holiday_flag, *_ = records[0]
    assert isinstance(store, int)
    assert isinstance(weekly_sales, float)
    assert isinstance(holiday_flag, bool)
