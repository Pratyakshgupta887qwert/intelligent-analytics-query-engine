import duckdb
from pathlib import Path

from app.data_loader import load_sales_data, load_targets_data


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "analytics.duckdb"


def create_database():
    """
    Create the DuckDB database and load the datasets.

    The sales order_date column is converted to a proper
    datetime type before being stored in DuckDB.
    """

    sales_df = load_sales_data()
    targets_df = load_targets_data()

    # Convert sales order_date to proper datetime type
    sales_df["order_date"] = sales_df["order_date"].astype("datetime64[ns]")

    connection = duckdb.connect(str(DB_PATH))

    # Replace tables if they already exist
    connection.execute("DROP TABLE IF EXISTS sales")
    connection.execute("DROP TABLE IF EXISTS targets")

    # Register Pandas DataFrames
    connection.register("sales_df", sales_df)
    connection.register("targets_df", targets_df)

    # Create DuckDB tables
    connection.execute("""
        CREATE TABLE sales AS
        SELECT * FROM sales_df
    """)

    connection.execute("""
        CREATE TABLE targets AS
        SELECT * FROM targets_df
    """)

    # Unregister temporary DataFrame references
    connection.unregister("sales_df")
    connection.unregister("targets_df")

    connection.close()


def get_connection():
    """
    Return a connection to the analytics database.
    """

    return duckdb.connect(str(DB_PATH))